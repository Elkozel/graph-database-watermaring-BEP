import matplotlib.pyplot as plt
import json
import os

def plot_documents_vs_time():
    data = ""
    with open('logs/results.json', 'r') as file:
        data = "[" + file.read().rstrip().replace('\n', ',') + "]"
        data = json.loads(data)
    watermark_data = [datapoint for datapoint in data if datapoint["action"] == "watermark"]
    watermark_data.sort(key=lambda x: x["documents_introduced"])
    # Generate points
    x1 = [datapoint["documents_introduced"] for datapoint in watermark_data]
    y1 = [datapoint["duration"] for datapoint in watermark_data]

    # plotting the line 1 points 
    plt.plot(x1, y1)
    
    # naming the x axis
    plt.xlabel('Number of pseudo documents')
    # naming the y axis
    plt.ylabel('Time for watermark')
    # giving a title to my graph
    plt.title('Time to watermark')
    plt.legend()

    return plt

def plot_percDel_vs_numNodes():
    data = ""
    with open('logs/results.json', 'r') as file:
        data = "[" + file.read().rstrip().replace('\n', ',') + "]"
        data = json.loads(data)
    deletion_data = [datapoint for datapoint in data if datapoint["action"] == "modification_attack"]
    deletion_data.sort(key=lambda x: x["num_watermarked_nodes"])
    # Generate points
    x1 = [datapoint["num_watermarked_nodes"] for datapoint in deletion_data]
    y1 = [datapoint["nodes_deleted"]/datapoint["nodes_before"] for datapoint in deletion_data]

    # plotting the line 1 points 
    plt.plot(x1, y1)
    
    # naming the x axis
    plt.xlabel('Number of watermarked documents')
    # naming the y axis
    plt.ylim([0,1])
    plt.ylabel('\% of nodes deleted')
    # giving a title to my graph
    plt.title('Watermark robustness')
    plt.legend()

    return plt

# Run if you only want to generate the plots
if __name__ == "__main__":
    plot_dir = "plots/"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plot1 = plot_documents_vs_time()
    plot1.savefig(os.path.join(plot_dir, "time_to_watermark.png"))
    plot2 = plot_percDel_vs_numNodes()
    plot2.savefig(os.path.join(plot_dir, "robustness.png"))
