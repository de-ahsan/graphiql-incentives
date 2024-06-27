import requests
import matplotlib.pyplot as plt
import datetime
from django.http import HttpResponse
from django.shortcuts import render
import io
import base64
import matplotlib

# Use the Agg backend for non-interactive plotting
matplotlib.use("Agg")


def fetch_and_plot_data():
    url = "https://api.taomarketcap.com/graphql"
    query = """
    query MyQuery {
      subnets(netUid: 18) {
        uids {
          incentive {
            uid
            data {
              value
              valueBlockNumber
              timestamp
              blockNumber
            }
          }
        }
      }
    }
    """
    response = requests.post(url, json={"query": query})
    response_data = response.json()

    # Check for the presence of data and subnets keys
    if "data" not in response_data or "subnets" not in response_data["data"]:
        return None

    data = response_data["data"]["subnets"]

    # Process the data
    incentives = []
    for subnet in data:
        for incentive_entry in subnet["uids"]["incentive"]:
            uid = incentive_entry["uid"]
            for incentive_data in incentive_entry["data"]:
                incentives.append(
                    {
                        "uid": uid,
                        "value": float(incentive_data["value"]),
                        "timestamp": datetime.datetime.strptime(
                            incentive_data["timestamp"], "%Y-%m-%d:%H:%M:%S"
                        ),
                    }
                )

    # Sort incentives by timestamp
    incentives.sort(key=lambda x: x["timestamp"])

    # Plot the data
    plt.figure(figsize=(20, 10))

    uids = set(i["uid"] for i in incentives)
    for uid in uids:
        uid_data = [i for i in incentives if i["uid"] == uid]
        timestamps = [i["timestamp"] for i in uid_data]
        values = [i["value"] for i in uid_data]
        plt.plot(timestamps, values, label=f"UID {uid}", alpha=0.7)

    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.title("Incentive Value Over Time for All UIDs on Subnet 18")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize="small")
    plt.grid(True)
    plt.xticks(rotation=45)

    # Set the y-axis limits to extend it
    plt.ylim(0, max(i["value"] for i in incentives) + 50)

    plt.tight_layout()

    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image to base64
    graph = base64.b64encode(image_png)
    graph = graph.decode("utf-8")

    return graph


def plot_view(request):
    graph = fetch_and_plot_data()
    if graph is None:
        return HttpResponse("Error fetching data", status=500)
    return render(request, "plot.html", {"graph": graph})

def home_view(request):
    return render(request, "home.html")
