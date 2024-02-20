Project for CS - 765 Blockchain.
Creating a Peer to Peer blockchain simulation network.

## Requirements:
- Python
- Graphviz for visualization of blockchain tree
- Numpy

## How to Run (steps):
In the project directory run:


```bash
python eventsim.py -nodes -slowNodes -lowCpuNodes -simTime -intArrTime
```

You can replace the arguments with the following:

- nodes : The number of peers in the network.
- slowNodes: The percentage of slow nodes.
- lowCpuNodes : The percentage of low CPU nodes.
- simTime : The total simulation time to run.
- intArrTime : Interarrival time of transaction.
