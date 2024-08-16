Project for CS - 765 Blockchain.
Creating a Peer to Peer blockchain simulation network.

## Requirements:
- Python
- Networkx
- Numpy
- Matplotlib
- uuid
- heapq

## How to Run (steps):
In the project directory run:


```bash
python3 main.py -nodes -slowNodes -lowCpuNodes -simTime -intArrTime -Adversary1Power -Adversary2Power
```

You can replace the arguments with the following:

- nodes : The number of peers in the network.
- slowNodes: The percentage of slow nodes.
- lowCpuNodes : The percentage of low CPU nodes.
- simTime : The total simulation time to run.
- intArrTime : Interarrival time of transaction.
- Adversary1Power : fraction of hashing power of adversary 1.
- Adversary2Power : fraction of hashing power of adversary 2.

