from db import CompetitionDatabase

db = CompetitionDatabase()

result = db.manual_query("Select * FROM results")

print(result)
