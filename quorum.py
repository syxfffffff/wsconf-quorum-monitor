
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

LIST_ID = os.environ["CLICKUP_LIST_ID"]
API_TOKEN = os.environ["CLICKUP_API_TOKEN"]
QUORUM = 87

def get_tasks():
    tasks = []
    page = 0

    while True:
        query = urllib.parse.urlencode({
            "include_closed": "true",
            "page": page
        })

        url = (
            f"https://api.clickup.com/api/v2/list/"
            f"{LIST_ID}/task?{query}"
        )

        request = urllib.request.Request(
            url,
            headers={
                "Authorization": API_TOKEN,
                "Accept": "application/json"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)

        batch = data.get("tasks", [])
        tasks.extend(batch)

        if len(batch) < 100:
            break

        page += 1

    return tasks


def main():
    tasks = get_tasks()

    votes_received = sum(
        1 for task in tasks
        if task.get("status", {}).get("status", "").lower()
        == "completed"
    )

    result = {
        "votes_received": votes_received,
        "quorum_required": QUORUM,
        "quorum_met": votes_received >= QUORUM,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

    os.makedirs("public", exist_ok=True)

    with open("public/quorum.json", "w") as file:
        json.dump(result, file, indent=2)

    print("Quorum calculation completed.")
    print("Votes received:", votes_received)
    print("Quorum met:", result["quorum_met"])


if __name__ == "__main__":
    main()
