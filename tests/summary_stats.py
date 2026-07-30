import sqlite3

conn = sqlite3.connect("data/raw_packages.db")
cursor = conn.cursor()

# Total rows
cursor.execute("SELECT COUNT(*) FROM packages")
total = cursor.fetchone()[0]
print(f"Total packages in database: {total}")

# Rows per category
print("\nPer category:")
cursor.execute("SELECT category, COUNT(*) FROM packages GROUP BY category")
for category, count in cursor.fetchall():
    print(f"  {category}: {count}")

# How many have complete GitHub data (stars is a good proxy)
cursor.execute("SELECT COUNT(*) FROM packages WHERE stars IS NOT NULL")
github_complete = cursor.fetchone()[0]
print(f"\nRows with GitHub data: {github_complete} ({github_complete/total*100:.1f}%)")

# How many have complete npm data (latest_version is a good proxy)
cursor.execute("SELECT COUNT(*) FROM packages WHERE latest_version IS NOT NULL")
npm_complete = cursor.fetchone()[0]
print(f"Rows with npm data: {npm_complete} ({npm_complete/total*100:.1f}%)")

# Rows with BOTH (our ideal, usable rows for modeling)
cursor.execute("SELECT COUNT(*) FROM packages WHERE stars IS NOT NULL AND latest_version IS NOT NULL")
both_complete = cursor.fetchone()[0]
print(f"Rows with BOTH GitHub + npm data: {both_complete} ({both_complete/total*100:.1f}%)")

conn.close()