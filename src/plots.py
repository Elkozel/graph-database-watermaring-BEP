import matplotlib.pyplot as plt
import numpy as np
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

    print("Documents per second: ", sum(x1)/sum(y1))

    # plotting the line 1 points 
    plt.plot(x1, y1)
    
    # naming the x axis
    plt.xlim(left=0)
    plt.xlabel('Number of pseudo documents')
    # naming the y axis
    plt.ylim(bottom=0)
    plt.ylabel('Time for watermark')
    # giving a title to my graph
    plt.title('Time to watermark')
    plt.legend()

    return plt

def plot_robustness():
    data = ""
    with open('logs/results.json', 'r') as file:
        data = "[" + file.read().rstrip().replace('\n', ',') + "]"
        data = json.loads(data)
    deletion_data = [datapoint for datapoint in data if datapoint["action"] == "deletion_attack"]
    deletion_data.sort(key=lambda x: x["num_watermarked_nodes"])
    # Generate points
    x1 = [datapoint["num_watermarked_nodes"] for datapoint in deletion_data]
    y1 = [datapoint["nodes_after"]*100/datapoint["nodes_before"] for datapoint in deletion_data]

    # plotting the line 1 points 
    plt.plot(x1, y1)
    # naming the x axis
    # plt.xlim(left=0)
    plt.xlabel('Number of watermarked documents')
    # naming the y axis
    plt.ylim([0,100])
    plt.ylabel('$\%$ of nodes deleted')
    # giving a title to my graph
    plt.title('Watermark robustness')
    plt.legend()

    return plt

def plot_usability():
    data = ""
    with open('logs/results.json', 'r') as file:
        data = "[" + file.read().rstrip().replace('\n', ',') + "]"
        data = json.loads(data)
    deletion_data = [datapoint for datapoint in data if datapoint["action"] == "deletion_attack"]
    deletion_data.sort(key=lambda x: x["num_watermarked_nodes"])
    # Generate points
    x1 = [datapoint["num_watermarked_nodes"]*100/datapoint["nodes_before"] for datapoint in deletion_data]
    y1 = [datapoint["nodes_after"]*100/datapoint["nodes_before"] for datapoint in deletion_data]

    # plotting the line 1 points 
    plt.plot(x1, y1)
    
    # naming the x axis
    plt.xlim(left=0)
    plt.xlabel('$\%$ of pseudo nodes')
    # naming the y axis
    plt.ylim([0,100])
    plt.ylabel('$\%$ of nodes deleted')
    # giving a title to my graph
    plt.title('Watermark robustness')
    plt.legend()

    return plt

def plot_parameter_diff():
    data = ""
    with open('logs/results.json', 'r') as file:
        data = "[" + file.read().rstrip().replace('\n', ',') + "]"
        data = json.loads(data)
    deletion_data = [datapoint for datapoint in data if datapoint["action"] == "watermark"]
    deletion_data.sort(key=lambda x: x["max_group_size"]-x["min_group_size"])
    # Generate points
    x1 = [datapoint["max_group_size"]-datapoint["min_group_size"] for datapoint in deletion_data]
    y1 = [datapoint["documents_introduced"] for datapoint in deletion_data]

    # plotting the line 1 points 
    plt.plot(x1, y1)
    
    # naming the x axis
    plt.xlabel('Difference between min and max parameter')
    # naming the y axis
    plt.ylabel('Documents introduced')
    # giving a title to my graph
    plt.title('Parameter Impact')
    plt.legend()

    return plt

def maybe_3d():
    data = ""
    with open('logs/results.json', 'r') as file:
        data = "[" + file.read().rstrip().replace('\n', ',') + "]"
        data = json.loads(data)
    deletion_data = [datapoint for datapoint in data if datapoint["action"] == "watermark"]
    # setup the figure and axes
    fig = plt.figure()
    ax1 = fig.add_subplot(121, projection='3d')

    # data
    _x = np.array([datapoint["min_group_size"] for datapoint in deletion_data])
    _y = np.arange([datapoint["max_group_size"] for datapoint in deletion_data])
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()

    top = x + y
    bottom = np.zeros_like(top)
    width = depth = 1

    ax1.bar3d(x, y, bottom, width, depth, top, shade=True)
    ax1.set_title('Shaded')

    plt.show()

def plot_security():
    data = ""
    with open('logs/results.json', 'r') as file:
        data = "[" + file.read().rstrip().replace('\n', ',') + "]"
        data = json.loads(data)
    deletion_data = [datapoint for datapoint in data if datapoint["action"] == "deletion_attack"]
    deletion_data.sort(key=lambda x: x["num_watermarked_nodes"])
    modification_data = [datapoint for datapoint in data if datapoint["action"] == "modification_attack"]
    modification_data.sort(key=lambda x: x["num_watermarked_nodes"])
    # Generate points
    x1 = [datapoint["num_watermarked_nodes"] for datapoint in deletion_data]
    y1 = [datapoint["nodes_after"]*100/datapoint["nodes_before"] for datapoint in deletion_data]
    NUM_OF_FIELDS = 324760
    x2 = [datapoint["num_watermarked_nodes"] for datapoint in modification_data]
    y2 = [datapoint["iteration"]/NUM_OF_FIELDS for datapoint in modification_data]

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Number of watermarked documents')
    ax1.set_ylim([0,100])
    ax1.set_ylabel('$\%$ of nodes deleted', color=color)
    ax1.plot(x1, y1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('number of fields modified', color=color)  # we already handled the x-label with ax1
    ax2.plot(x2, y2, color=color)
    ax2.set_ylim([0,324760])
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
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
    plt.cla()
    plt.clf()
    plot2 = plot_robustness()
    plot2.savefig(os.path.join(plot_dir, "robustness.png"))
    plt.cla()
    plt.clf()
    plot3 = plot_usability()
    plot3.savefig(os.path.join(plot_dir, "usability.png"))
    plt.cla()
    plt.clf()
    plot4 = plot_parameter_diff()
    plot4.savefig(os.path.join(plot_dir, "param_diff.png"))
    plt.cla()
    plt.clf()
    plot5 = plot_security()
    plot5.savefig(os.path.join(plot_dir, "security.png"))

