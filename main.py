import heapq
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import uuid

eventQueue=[]

class Peer: 
    def __init__(self, peer_id, is_slow, is_low_cpu):
        self.peer_id = peer_id
        self.is_slow = is_slow
        self.is_low_cpu = is_low_cpu
        self.connected_peers = set()
        self.coins=100

    def __repr__(self):
        return f"Peer {self.peer_id} ({'slow' if self.is_slow else 'fast'}, {'low CPU' if self.is_low_cpu else 'high CPU'})"

class Block:
    def __init__ (self,blockid,parentid,txnIncluded):
        self.blockid=blockid
        self.parentid=parentid
        self.txnIncluded=txnIncluded



class Event:
    def __init__(self, time, event_type,sender=None, receiver=None,  transaction=None, block=None):
        self.time = time
        self.sender = sender
        self.receiver = receiver
        self.event_type = event_type
        self.transaction = transaction
        self.block= block

    def __lt__(self, other):
        return self.time < other.time
    
class Transaction:
    def __init__(self, txn_id, sender_id, receiver_id, coins):
        self.txn_id = txn_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.coins = coins

class NetworkSimulator:
    def __init__(self, num_peers, slow_percent, low_cpu_percent, meanInterarrivalTime):
        self.peers = []
        self.event_queue = []
        self.time = 0
        self.num_peers = num_peers
        self.slow_percent = slow_percent
        self.low_cpu_percent = low_cpu_percent
        self.numSlow= int((self.slow_percent*num_peers)/100)
        self.numFast= num_peers-self.numSlow
        self.numLowCpu= int((self.slow_percent*num_peers)/100)
        self.numHighCpu= num_peers-self.numLowCpu
        self.meanInterarrivalTime= meanInterarrivalTime

        speedList = [True] * self.numSlow + [False] * self.numFast
        random.shuffle(speedList)

        cpuList = [True] * self.numLowCpu + [False] * self.numHighCpu
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

    
    def generateTransactions(self, simulationTime, sender):
        temp = [item for item in self.peers if item != sender]
        t_curr=np.random.exponential(self.meanInterarrivalTime)
        while t_curr<simulationTime:
            if sender.coins>0:
                coinsSent=random.randint(1,sender.coins)
                transaction=Transaction(uuid.uuid4(),
                                        sender, 
                                        random.choice(temp), 
                                        coinsSent)
                sender.coin=sender.coins-coinsSent
                heapq.heappush(eventQueue,(t_curr,Event(t_curr,
                                                        "transaction",
                                                        transaction.sender_id,
                                                        transaction.receiver_id, 
                                                        transaction)))
                t_curr=t_curr+np.random.exponential(self.meanInterarrivalTime)
            else:
                break
                

        
        
    
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
            connected_nodes = self.peers[i].connected_peers
            while len(self.peers[i].connected_peers) < num_connections:
                connected_node = random.randint(0, num_peers - 1)
                if connected_node != i and connected_node not in self.peers[i].connected_peers and len(self.peers[connected_node].connected_peers)<6:
                    # delay=random.uniform(10,500) 
                    # G.add_edge(i, connected_node,delay=delay)
                    G.add_edge(i, connected_node)
                    self.peers[i].connected_peers.add(self.peers[connected_node])
                    self.peers[connected_node].connected_peers.add(self.peers[i])
            # for index in connected_nodes:
            #     self.peers[i].connected_peers.add(self.peers[index])
            # self.peers[i].connected_peers=connected_nodes
            # self.peers[i].peer_id=i
        self.edge_latencies={}
        for edge in G.edges():
            sender=edge[0]
            receiver=edge[1]
            node1=self.peers[sender]
            node2=self.peers[receiver]
            cij=0
            if node1.is_slow or node2.is_slow:
                cij=5000   #kbps
            else:
                cij=100000  #kbps 
            propDelay=random.uniform(0.01,0.5) #Propagation delay(ρij)
            dij=np.random.exponential(96/cij)
            totalDelay=dij+propDelay
            self.edge_latencies[(sender,receiver)]=totalDelay
            # pos = nx.spring_layout(G)
            # nx.draw_networkx_edge_labels(G, pos, edge_labels={(sender, receiver): f"{totalDelay:.6f}s"})
        
        nx.draw(G,with_labels=True)
        # pos = nx.spring_layout(G)
        # edge_labels = nx.get_edge_attributes(G, 'delay')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.savefig("Graph.png")
        
    def genTransaction(self):
        sender=random.choice(num_peers)
        receiver=random.choice(num_peers)
        
        coins_available = random.randint(1, 100)
        coins_to_transfer = random.randint(1, coins_available)
        # Generate transaction string
        transaction = f"TxnID: {sender} pays {receiver} {coins_to_transfer} coins"

        return transaction



if __name__ == "__main__":
    num_peers = 7
    slow_percent = 20
    low_cpu_percent = 30
    simulation_time = 20
    meanInterarrivalTime=5

    network_simulator = NetworkSimulator(num_peers, slow_percent, low_cpu_percent, meanInterarrivalTime)
    for peer in network_simulator.peers:
        network_simulator.generateTransactions(simulation_time, peer)
    print(eventQueue)

    

    network_simulator.graphGenerator()
    network_simulator.run_simulation(simulation_time)
    print(network_simulator.edge_latencies)
