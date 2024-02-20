import heapq
import random
import networkx as nx  ## for drawing graphs for visualization
import matplotlib.pyplot as plt
import numpy as np
import uuid  ## for assigning unique id's

eventQueue=[]  ## queue to store all events


## Class for diffrent nodes or peers

class Peer: 
    def __init__(self, peer_id, is_slow, is_low_cpu, hashPower):
        self.peer_id = peer_id
        self.is_slow = is_slow
        self.is_low_cpu = is_low_cpu
        self.connected_peers = set()
        self.coins=100
        self.hashPower=hashPower
        self.transactions=[]

    def __repr__(self):
        return f"Peer {self.peer_id} ({'slow' if self.is_slow else 'fast'}, {'low CPU' if self.is_low_cpu else 'high CPU'})"


## Class for each event         

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
    
## Class for diffrent transactions

class Transaction:
    def __init__(self, txn_id, sender, receiver, coins):
        self.txn_id = txn_id
        self.sender = sender
        self.receiver = receiver
        self.coins = coins

## The Main simulator class

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
        self.hash= 10/(10*self.num_peers-9*self.numLowCpu)


        ## Create nodes or neighbours or peers
        for i in range(num_peers):
            is_slow = speedList[i]
            is_low_cpu = cpuList[i]
            hashPower= self.hash/10 if is_low_cpu else self.hash
            peer = Peer(i, is_slow, is_low_cpu, hashPower)
            self.peers.append(peer)


        
        # Connect peers randomly
        # for i in range(num_peers):
        #     num_connections = random.randint(1, num_peers)
        #     connected_peers = random.sample(range(num_peers), num_connections)
        #     for j in connected_peers:
        #         if j != i:
        #             self.peers[i].connected_peers.add(self.peers[j])
        
        print(self.peers)

    
    ## This function generates the transactions for each node to diffrent node 

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
                                                        "transactionSend",
                                                        transaction.sender,
                                                        transaction.receiver, 
                                                        transaction)))
                t_curr=t_curr+np.random.exponential(self.meanInterarrivalTime)
            else:
                break
                
    ## Function to generate blocks based on hashing power

    def generateBlocks(self, I=600):
        for i in self.peers:
            t=np.random.exponential(I/i.hashPower)
            block= Block(uuid.uuid4(),
                         genesis.id,
                         Transaction(uuid.uuid4(),
                                     None,
                                     i,
                                     50),
                                     i)
            heapq.heappush(eventQueue, (t, Event(t,"blockMine",block=block)))
        
    
    def schedule_event(self, time, peer, event_type, data=None):
        event = Event(time, peer, event_type, data)
        heapq.heappush(self.event_queue, event)

        
    def run_simulation(self, simulationTime):
        time=0
        while eventQueue.__len__ and time<simulationTime:
            time, event= heapq.heappop(eventQueue)
            self.propagate(event,time)

    ## We can tell it as a broadcast function which propogates a transaction info into the network

    def propagate(self,event,time):
        if event.event_type=="transactionSend":
            event.transaction.sender.transactions.append(event.transaction)
            for i in event.sender.connected_peers:
                t=time
                latency=self.calculateLatency(event.sender,i,"transaction")
                t+=latency
                heapq.heappush(eventQueue,(t,Event(t,
                                                   "transactionReceive",
                                                   event.sender,
                                                   i,
                                                   event.transaction)))
        
        elif event.event_type=="transactionReceive":
            sender=event.receiver
            if event.transaction not in sender.transactions:
                sender.transactions.append(event.transaction)
                for i in event.sender.connected_peers:
                    t=time
                    latency=self.calculateLatency(event.sender,i,"transaction")
                    t+=latency
                    heapq.heappush(eventQueue,(t,Event(t,
                                                       "transactionReceive",
                                                       sender,
                                                       i,
                                                       event.transaction)))



    ## Generates the graph for our Peer to Peer network using the networkx library
    def graphGenerator(self):
        self.G = nx.Graph()
        G=self.G

        ## Add nodes to the graph
        for i in range(num_peers):
            G.add_node(i)

        ## Randomly connect nodes
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
        # self.edge_latencies=[]
        # for edge in G.edges():
        #     sender=edge[0]
        #     receiver=edge[1]
        #     node1=self.peers[sender]
        #     node2=self.peers[receiver]
        #     cij=0
        #     if node1.is_slow or node2.is_slow:
        #         cij=5000   #kbps
        #     else:
        #         cij=100000  #kbps 
        #     propDelay=random.uniform(0.01,0.5) #Propagation delay(ρij)
        #     dij=np.random.exponential(96/cij)
        #     totalDelay=dij+propDelay
        #     self.edge_latencies[(sender,receiver)]=totalDelay
            # pos = nx.spring_layout(G)
            # nx.draw_networkx_edge_labels(G, pos, edge_labels={(sender, receiver): f"{totalDelay:.6f}s"})
        
        nx.draw(G,with_labels=True)
        # pos = nx.spring_layout(G)
        # edge_labels = nx.get_edge_attributes(G, 'delay')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.savefig("Graph.png")
    
    ## Function to calculate latency based on the three parameters given in the 
    ## assignment document.
    
    def calculateLatency(self,sender,receiver,type):
            node1=sender
            node2=receiver
            cij=0
            if node1.is_slow or node2.is_slow:
                cij=5000                           #kbps
            else:
                cij=100000                         #kbps 
            propDelay=random.uniform(0.01,0.5)     #Propagation delay(ρij)
            dij=np.random.exponential(96/cij)
            mij=8/cij if type=="Txn" else 8000/cij #message delay as given in question
            totalDelay=dij+propDelay+mij
            return totalDelay

if __name__ == "__main__":
    num_peers = 7
    slow_percent = 20
    low_cpu_percent = 30
    simulation_time = 20
    meanInterarrivalTime=5

    genesis=Block(uuid.uuid4(),0,None)

    network_simulator = NetworkSimulator(num_peers, slow_percent, low_cpu_percent, meanInterarrivalTime)
    for peer in network_simulator.peers:
        network_simulator.generateTransactions(simulation_time, peer)

    

    network_simulator.graphGenerator()
    network_simulator.run_simulation(simulation_time)
    print(eventQueue)
    # print(network_simulator.edge_latencies)
