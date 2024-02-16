import heapq
import random
import networkx as nx
import matplotlib.pyplot as plt
class Peer: 
    def __init__(self, peer_id, is_slow, is_low_cpu):
        self.peer_id = peer_id
        self.is_slow = is_slow
        self.is_low_cpu = is_low_cpu
        self.connected_peers = set()

    def __repr__(self):
        return f"Peer {self.peer_id} ({'slow' if self.is_slow else 'fast'}, {'low CPU' if self.is_low_cpu else 'high CPU'})"

class Event:
    def __init__(self, time, peer, event_type, data=None):
        self.time = time
        self.peer = peer
        self.event_type = event_type
        self.data = data

    def __lt__(self, other):
        return self.time < other.time

class NetworkSimulator:
    def __init__(self, num_peers, slow_percent, low_cpu_percent):
        self.peers = []
        self.event_queue = []
        self.time = 0
        self.num_peers = num_peers
        self.slow_percent = slow_percent
        self.low_cpu_percent = low_cpu_percent
        self.numSlow= (self.slow_percent*num_peers)/100
        self.numFast= num_peers-self.numSlow
        self.numLowCpu= (self.slow_percent*num_peers)/100
        self.numHighCpu= num_peers-self.numLowCpu

        speedList = [True] * int(self.numSlow) + [False] * int(self.numFast)
        random.shuffle(speedList)

        cpuList = [True] * int(self.numLowCpu) + [False] * int(self.numHighCpu)
        random.shuffle(cpuList)

        # Create peers
        for i in range(num_peers):
            is_slow = speedList[i]
            is_low_cpu = cpuList[i]
            peer = Peer(i, is_slow, is_low_cpu)
            self.peers.append(peer)

        
            # Connect peers randomly
        # for i in range(num_peers):
        #     num_connections = random.randint(1, num_peers)
        #     connected_peers = random.sample(range(num_peers), num_connections)
        #     for j in connected_peers:
        #         if j != i:
        #             self.peers[i].connected_peers.add(self.peers[j])
        
        print(self.peers)

    def schedule_event(self, time, peer, event_type, data=None):
        event = Event(time, peer, event_type, data)
        heapq.heappush(self.event_queue, event)

    def run_simulation(self, end_time):
        while self.time < end_time:
            if not self.event_queue:
                break
            event = heapq.heappop(self.event_queue)
            self.time = event.time
            if event.event_type == "send_block":
                receiver = random.choice(list(event.peer.connected_peers))
                transmission_delay = random.uniform(0.1, 1.0) if event.peer.is_slow else random.uniform(0.01, 0.1)
                self.schedule_event(self.time + transmission_delay, receiver, "receive_block")
                print(f"At time {self.time}: Peer {event.peer.peer_id} sends block to Peer {receiver.peer_id}")
            elif event.event_type == "receive_block":
                print(f"At time {self.time}: Peer {event.peer.peer_id} receives block")
            else:
                print(f"Unknown event type: {event.event_type}")
    
    def graphGenerator(self):
        G = nx.Graph()

        # Add nodes to the graph
        for i in range(num_peers):
            G.add_node(i)

        # Randomly connect nodes
        for i in range(num_peers):
            num_connections = random.randint(3, 6)
            connected_nodes = set()
            while len(connected_nodes) < num_connections:
                connected_node = random.randint(0, num_peers - 1)
                if connected_node != i and connected_node not in connected_nodes:
                    G.add_edge(i, connected_node)
                    connected_nodes.add(connected_node)
            for index in connected_nodes:
                self.peers[i].connected_peers.add(self.peers[index])
            # self.peers[i].connected_peers=connected_nodes
            # self.peers[i].peer_id=i
        
        nx.draw(G)
        plt.savefig("Graph.png")

if __name__ == "__main__":
    num_peers = 10
    slow_percent = 20
    low_cpu_percent = 30
    simulation_time = 10

    network_simulator = NetworkSimulator(num_peers, slow_percent, low_cpu_percent)
    for peer in network_simulator.peers:
        network_simulator.schedule_event(0, peer, "send_block")
    

    

    network_simulator.graphGenerator()
    network_simulator.run_simulation(simulation_time)
