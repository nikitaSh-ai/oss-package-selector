import requests
import time




# Hand-picked canonical packages per category — ensures well-known
# packages are always included, since keyword-tag search alone
# misses them (many popular packages don't self-tag consistently).
SEED_PACKAGES = {
    "HTTP clients": ["axios", "node-fetch", "got", "superagent", "ky", "undici"],
    "Date/time libraries": ["moment", "dayjs", "date-fns", "luxon"],
    "Testing frameworks": ["jest", "mocha", "vitest", "ava", "jasmine", "tape"],
    "State management": ["redux", "zustand", "mobx", "recoil", "jotai", "xstate"],
    "Utility libraries": ["lodash", "ramda", "underscore"],
    "Data validation": ["zod", "yup", "joi", "ajv", "superstruct"],
}



CATEGORY_QUERIES = {
    "HTTP clients": "keywords:http-client",
    "Date/time libraries": "keywords:date",
    "Testing frameworks": "keywords:testing-framework",
    "State management": "keywords:state-management",
    "Utility libraries": "keywords:utility",
    "Data validation": "keywords:validation",
}

RESULTS_PER_CATEGORY = 60  # aim for ~360 total across 6 categories


def search_npm(query: str, size: int = 60, min_popularity: float = 0.0) -> list:
    """search npm registry, return package names filtered by popularity score."""
    url = "https://registry.npmjs.org/-/v1/search"
    params = {"text": query, "size": size}
    response = requests.get(url, params=params, timeout=15)

    if response.status_code != 200:
        print(f"⚠️ Search failed for '{query}': {response.status_code}")
        return []

    data = response.json()
    results = []
    for obj in data.get("objects", []):
        popularity = obj.get("score", {}).get("detail", {}).get("popularity", 0)
        if popularity >= min_popularity:
            results.append(obj["package"]["name"])

    return results


def discover_all_packages() -> list:
    """Combine seed packages with keyword-discovered packages per category."""
    all_packages = []
    seen_names = set()

    for category, query in CATEGORY_QUERIES.items():
        print(f"Processing: {category}")

        # 1. Add seeds first
        for name in SEED_PACKAGES.get(category, []):
            if name not in seen_names:
                all_packages.append({"name": name, "category": category})
                seen_names.add(name)

        seed_count = len(SEED_PACKAGES.get(category, []))
        print(f"  → {seed_count} seed packages added")

        # 2. Fill in with keyword-discovered packages
        names = search_npm(query, size=60)
        added = 0
        for name in names:
            if name not in seen_names:
                all_packages.append({"name": name, "category": category})
                seen_names.add(name)
                added += 1

        print(f"  → {added} discovered packages added")
        time.sleep(0.5)

    return all_packages




if __name__ == "__main__":
    packages = discover_all_packages()
    print(f"\n✅ Total packages discovered: {len(packages)}")

    # Save to a JSON file for reproducibility
    import json
    with open("data/discovered_packages.json", "w") as f:
        json.dump(packages, f, indent=2)
    print("✅ Saved to data/discovered_packages.json")

    from collections import defaultdict
    by_category = defaultdict(list)
    for pkg in packages:
        by_category[pkg["category"]].append(pkg["name"])

    for cat, names in by_category.items():
        print(f"\n{cat} ({len(names)} total):")
        print(" ", names[:5])