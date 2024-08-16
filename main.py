import sys
import heapq
import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import uuid
from matplotlib.animation import FuncAnimation


from blockchainTree import TreeNode

globalGraph=nx.Graph()


##queue for pushing events for transactions and blocks.
eventQueue=[]

class Peer: 
    def __init__(self, peer_id, is_slow, is_low_cpu, hashPower, type):
        self.peer_id = peer_id
        self.type=type
        self.is_slow = is_slow
        self.is_low_cpu = is_low_cpu
        self.connected_peers = set()
        self.coins=100
        self.hashPower=hashPower
        self.transactions=[]
        self.lastBlock=genesis
        self.blockchain=[genesis]
        self.root=TreeNode(genesis)
        self.blockReceived=[]
        self.waitlist=[]
        self.graph=nx.Graph()
        self.graph.add_node(genesis.blockid, node_color='green', attribute=0)
        globalGraph.add_node(genesis.blockid, node_color='green', attribute=0)
        if self.type=="attacker":
            self.privateChain=[]
            self.isZeroDash=False

    def mineBlocks(self,lastBlock,time):
     # Calculate the number of transactions to include in the block
        if len(self.transactions) ==0 or self.hashPower==0:
            return
        num=999 if len(self.transactions)>999 else len(self.transactions)
        txns= random.sample(self.transactions, num)
        coinbaseTxn= Transaction(uuid.uuid4(),None,self,50)
        txns.append(coinbaseTxn)
        self.lastBlock=lastBlock
        # Calculate the time for block mining based on hash power
        t=time+(np.random.exponential(600/self.hashPower) if self.hashPower>0 else simulation_time+1)  ## Time for block mining (adjusted for hash power)
        block= Block(uuid.uuid4(),
                         lastBlock.blockid,
                         txns,
                         self)
        heapq.heappush(eventQueue, (t, Event(t,"blockMine",block=block)))
        allBlocks[block.blockid]=block


    # def __repr__(self):
    #     return f"Peer {self.peer_id} ({'slow' if self.is_slow else 'fast'}, {'low CPU' if self.is_low_cpu else 'high CPU'})"

class Block:
	##class for creating a block
    def __init__ (self,blockid,parentid,txnIncluded=None,miner=None):
        self.blockid=blockid
        self.parentid=parentid
        self.txnIncluded=txnIncluded
        self.miner=miner
        self.balance=[]
        self.length=allBlocks[self.parentid].length+1 if self.parentid!=0 else 1

    ##function to handle block events
    
    def handleBlockEvent(self,event,time):

        miner=event.block.miner
        
        ##For blockmine event one more condition is there to receive block
        if event.event_type=="blockMine":
        
        ##Case for honest miners
            if miner.type=="honest":     
                if self.length>miner.lastBlock.length:
                    miner.graph.add_node(self.blockid, node_color='blue', attribute=time)
                    miner.graph.add_edge(self.parentid,self.blockid)
                    globalGraph.add_node(self.blockid, node_color='blue', attribute=time)
                    globalGraph.add_edge(self.parentid,self.blockid)
                    miner.lastBlock=self
                    miner.blockchain.append(self)
                    miner.blockReceived.append(self)
                    miner.root.add_child(TreeNode(self))
                    # Assuming miner.transactions is a list
                    miner.transactions = [t for t in miner.transactions if t not in self.txnIncluded]

                    for i in miner.connected_peers:
                        t=time
                        latency=network_simulator.calculateLatency(miner,i,"block")
                        t+=latency
                        heapq.heappush(eventQueue,(t,Event(t,
                                                        "blockReceive",
                                                        miner,
                                                        i,
                                                        block=self)))
                        # print(f"Block mined by {miner}. Now sending to {i}\n")
                        
                    miner.mineBlocks(self,time)

            else:
            ##Case for attacker
                if self.length>miner.lastBlock.length:
                    miner.graph.add_node(self.blockid, node_color='red' if miner.peer_id==num_peers-1 else 'black', attribute=time)
                    miner.graph.add_edge(self.parentid,self.blockid)
                    globalGraph.add_node(self.blockid, node_color='red' if miner.peer_id==num_peers-1 else 'black', attribute=time)
                    globalGraph.add_edge(self.parentid,self.blockid)
                    miner.lastBlock=self
                    miner.privateChain.append(self)
                    miner.blockchain.append(self)
                    miner.blockReceived.append(self)
                    miner.root.add_child(TreeNode(self))
                    # Assuming miner.transactions is a list
                    miner.transactions = [t for t in miner.transactions if t not in self.txnIncluded]

                    if miner.isZeroDash:
                        miner.privateChain.pop(0)
                        for i in miner.connected_peers:
                            t=time
                            latency=network_simulator.calculateLatency(miner,i,"block")
                            t+=latency
                            heapq.heappush(eventQueue,(t,Event(t,
                                                            "blockReceive",
                                                            miner,
                                                            i,
                                                            block=self)))
                            # print(f"Block mined by {miner}. Now sending to {i}\n")
                            
                    miner.mineBlocks(self,time)

            
            ##event for block receive
            
        elif event.event_type=="blockReceive":
            receiver= event.receiver
            if receiver.type=="honest":
                if self not in receiver.blockReceived:
                    receiver.blockReceived.append(self)
                    # if allBlocks[self.parentid] not in receiver.blockchain:
                    #     # receiver.addBlocks(self)
                    #     return
                    receiver.graph.add_node(self.blockid, node_color='red' if miner.peer_id==num_peers-1 else ('black' if miner.peer_id==num_peers-2 else 'blue'),attribute=time)
                    receiver.graph.add_edge(self.blockid, self.parentid)
                    globalGraph.add_node(self.blockid, node_color='red' if miner.peer_id==num_peers-1 else ('black' if miner.peer_id==num_peers-2 else 'blue'),attribute=time)
                    globalGraph.add_edge(self.blockid, self.parentid)
                    if self.length>receiver.lastBlock.length:
                        for i in receiver.connected_peers:
                            t=time
                            latency=network_simulator.calculateLatency(receiver,i,"block")
                            t+=latency
                            heapq.heappush(eventQueue,(t,Event(t,
                                                            "blockReceive",
                                                            receiver,
                                                            i,
                                                            block=self)))
                            # print(f"{receiver.type}Block received by {receiver}. Now sending to {i}\n")

                        # print("--------------------------------------------")
                            
                        receiver.mineBlocks(self,time)

            else:
                if self not in receiver.blockReceived:
                    receiver.blockReceived.append(self)
                    # if allBlocks[self.parentid] not in receiver.blockchain:
                    #     # receiver.addBlocks(self)
                    #     return
                    receiver.graph.add_node(self.blockid, node_color='red' if miner.peer_id==num_peers-1 else ('black' if miner.peer_id==num_peers-2 else 'blue'),attribute=time)
                    receiver.graph.add_edge(self.blockid, self.parentid)
                    globalGraph.add_node(self.blockid, node_color='red' if miner.peer_id==num_peers-1 else ('black' if miner.peer_id==num_peers-2 else 'blue'),attribute=time)
                    globalGraph.add_edge(self.blockid, self.parentid)
                    if len(receiver.privateChain)==0:
                        receiver.mineBlocks(self,time)
                    
                    elif self.length==receiver.privateChain[0].length and len(receiver.privateChain)>2:
                        block=receiver.privateChain.pop(0)
                        for i in receiver.connected_peers:
                            t=time
                            latency=network_simulator.calculateLatency(receiver,i,"block")
                            t+=latency
                            heapq.heappush(eventQueue,(t,Event(t,
                                                            "blockReceive",
                                                            receiver,
                                                            i,
                                                            block=block)))
                            # print(f"Block received by {miner}. Now sending to {i}\n")
                        receiver.mineBlocks(receiver.lastBlock,time)

                    elif self.length==receiver.privateChain[0].length and len(receiver.privateChain)==2:
                        block1=receiver.privateChain.pop(0)
                        block2=receiver.privateChain.pop(0)
                        for i in receiver.connected_peers:
                            t=time
                            latency=network_simulator.calculateLatency(receiver,i,"block")
                            t+=latency
                            heapq.heappush(eventQueue,(t,Event(t,
                                                            "blockReceive",
                                                            receiver,
                                                            i,
                                                            block=block1)))
                            heapq.heappush(eventQueue,(t,Event(t,
                                                            "blockReceive",
                                                            receiver,
                                                            i,
                                                            block=block2)))
                            # print(f"Block received by {miner}. Now sending to {i}\n")
                        receiver.mineBlocks(receiver.lastBlock,time)

                    elif self.length==receiver.privateChain[0].length and len(receiver.privateChain)==1:
                        receiver.isZeroDash=True
                        block=receiver.privateChain.pop(0)
                        for i in receiver.connected_peers:
                            t=time
                            latency=network_simulator.calculateLatency(receiver,i,"block")
                            t+=latency
                            heapq.heappush(eventQueue,(t,Event(t,
                                                            "blockReceive",
                                                            receiver,
                                                            i,
                                                            block=block)))
                            # print(f"Block received by {miner}. Now sending to {i}\n")
                        receiver.mineBlocks(receiver.lastBlock,time)



##Handles all event regarding block creation and all.
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
    
##Handle event regarding Transactions.
class Transaction:
    def __init__(self, txn_id, sender, receiver, coins):
        self.txn_id = txn_id
        self.sender = sender
        self.receiver = receiver
        self.coins = coins

##Class to create peers and simulate different cases for the project.
class NetworkSimulator:
    def __init__(self, num_peers, slow_percent, low_cpu_percent, meanInterarrivalTime, attacker1Hash, attacker2Hash):
        self.propDelay=random.uniform(0.01,0.5) #Propagation delay(ρij)
        self.peers = []
        self.event_queue = []
        self.time = 0
        self.num_peers = num_peers
        honestPeers=num_peers-2
        self.slow_percent = slow_percent
        self.low_cpu_percent = low_cpu_percent
        self.numSlow= int((self.slow_percent*honestPeers)/100)
        self.numFast= honestPeers-self.numSlow
        self.numLowCpu= int((self.slow_percent*honestPeers)/100)
        self.numHighCpu= honestPeers-self.numLowCpu
        self.meanInterarrivalTime= meanInterarrivalTime

        speedList = [True] * self.numSlow + [False] * self.numFast
        random.shuffle(speedList)

        cpuList = [True] * self.numLowCpu + [False] * self.numHighCpu
        random.shuffle(cpuList)
        self.hash= (1-attacker1Hash-attacker2Hash)/(10*honestPeers-9*self.numLowCpu)


        # Create peers
        for i in range(honestPeers):
            is_slow = speedList[i]
            is_low_cpu = cpuList[i]
            hashPower= self.hash if is_low_cpu else self.hash*10
            peer = Peer(i, is_slow, is_low_cpu, hashPower, "honest")
            self.peers.append(peer)
        self.peers.append(Peer(honestPeers,False,False,attacker1Hash,"attacker"))
        self.peers.append(Peer(honestPeers+1,False,False,attacker2Hash,"attacker"))

    
    ##Generating transaction
    
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
                

	##Function for generating Blocks
	
    def generateBlocks(self):
        I=600
        for i in self.peers:
            if i.hashPower==0:
                continue
            t=np.random.exponential(I/i.hashPower) if i.hashPower >0 else simulation_time+1
            block= Block(uuid.uuid4(),
                         genesis.blockid,
                         [Transaction(uuid.uuid4(),
                                     None,
                                     i,
                                     50)],
                                     i)
            # print(f"{i} started mining block.")
            heapq.heappush(eventQueue, (t, Event(t,"blockMine",block=block)))
            allBlocks[block.blockid]=block
        
    	##Function to schedule events
    	
    def schedule_event(self, time, peer, event_type, data=None):
        event = Event(time, peer, event_type, data)
        heapq.heappush(self.event_queue, event)

        ##Function for running simulation
        
    def run_simulation(self, simulationTime):
        time=0
        while eventQueue:
            time, event= heapq.heappop(eventQueue)
            if event.event_type in ["transactionSend","transactionReceive"]:
                self.propagate(event,time)
            else:
                # print(f"{event.receiver} {event.sender} {event.block} {event.event_type}")
                event.block.handleBlockEvent(event,time)

    ##This function is used to propagate event to different peers.
    
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
            # print(f"Transaction initiated by {event.sender}. Now propagating to {event.sender.connected_peers}\n")

        
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
                # print(f"Transaction received by {sender}. Now propagating to {sender.connected_peers}\n")


    def graphGenerator(self):
        self.G = nx.Graph()
        G=self.G

        # Add nodes to the graph
        for i in range(num_peers):
            G.add_node(i)

        # Randomly connect nodes
        while True:
            G.remove_edges_from(list(G.edges()))
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

            if nx.is_connected(G):
                break
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
        pos = nx.spring_layout(G)
        # edge_labels = nx.get_edge_attributes(G, 'delay')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.savefig("Graph.png")


    def generate_connected_graph(self):
        # Create an empty graph
        self.G = nx.Graph()
        G=self.G

        # Add all nodes to the graph
        for i in range(num_peers):
            G.add_node(i)

        while True:
            # Reset the graph
            G.remove_edges_from(list(G.edges()))

            # Connect each peer to a random number of other peers
            for i in range(num_peers):
                num_connections = random.randint(3, 6)
                while len(self.peers[i].connected_peers) < num_connections:
                    connected_node = self.peers[random.randint(0, num_peers - 1)]
                    if connected_node != self.peers[i] and connected_node not in self.peers[i].connected_peers:
                        G.add_edge(i, connected_node.peer_id)
                        self.peers[i].connected_peers.add(connected_node)

            # Check if the graph is connected
            if nx.is_connected(G):
                break
        # nx.draw(G,with_labels=True)
        # pos = nx.spring_layout(G)
        # plt.savefig("Graph.png")

        # edge_labels = nx.get_edge_attributes(G, 'delay')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    
    def calculateLatency(self,sender,receiver,type):
            node1=sender
            node2=receiver
            cij=0
            if node1.is_slow or node2.is_slow:
                cij=5000   #kbps
            else:
                cij=100000  #kbps 
            dij=np.random.exponential(96/cij)
            # print(f"dij={dij}\n")
            mij=8/cij if type=="transaction" else 8000/cij #message delay as given in question
            # print(f"mij={mij}  dij={dij} p={self.propDelay}\n")
            totalDelay=dij+self.propDelay+mij
            return totalDelay



if __name__ == "__main__":
    ## number of nodes
    num_peers = int(sys.argv[1])

    ## percentage of slow nodes
    slow_percent = int(sys.argv[2])

    ## percentage of low cpu nodes
    low_cpu_percent = int(sys.argv[3])

    ## total time to run the simulation for
    simulation_time = int(sys.argv[4])

    ## interarrival time for transactions
    meanInterarrivalTime= int(sys.argv[5])
    
    ## hashPower of attacker1
    attacker1Hash= float(sys.argv[6])
    
    ## hashPower of attacker2
    attacker2Hash= float(sys.argv[7])

    
    allBlocks={}
    genesis=Block(uuid.uuid4(),0,None)
    allBlocks[genesis.blockid]=genesis

    network_simulator = NetworkSimulator(num_peers, slow_percent, low_cpu_percent, meanInterarrivalTime, attacker1Hash, attacker2Hash)
    network_simulator.graphGenerator()
    for peer in network_simulator.peers:
        network_simulator.generateTransactions(simulation_time, peer)
        peers=[p.peer_id for p in peer.connected_peers]
        print(peers)

    network_simulator.generateBlocks()
    

    network_simulator.run_simulation(simulation_time)
    # chainGraph=network_simulator.peers[9].graph
    # node_colors = [node_data['node_color'] for node, node_data in chainGraph.nodes(data=True)]
    # # print(node_colors)
    # node_labels = {node: node_data['attribute'] for node, node_data in chainGraph.nodes(data=True)}
    # plt.figure()
    # pos = nx.kamada_kawai_layout(chainGraph)  # Positions of the nodes
    # nx.draw(chainGraph, pos, with_labels=False, labels=node_labels, arrows=True, node_color=node_colors)  # Draw the graph with arrows and without labels
    # plt.savefig("chain.png")
    # plt.show()


    # def blockchain_layout(G):
    #     pos = {}
    #     x = 0
    #     y = 0
    #     dx = 1  # Horizontal spacing between nodes
    #     dy = 1  # Vertical spacing between nodes
    #     for node in G.nodes():
    #         pos[node] = (x, y)
    #         x += dx
    #         y = (-y + dy) % (2 * dy) - dy  # Zigzag pattern
    #     return pos


    chainGraph1 = globalGraph
    chainGraph2 = network_simulator.peers[9].graph
    # if nx.is_connected(chainGraph1) and nx.is_connected(chainGraph2):    
    for node in chainGraph1.nodes():
        if 'node_color' not in chainGraph1.nodes[node]:
            miner=allBlocks[node].miner
            chainGraph1.nodes[node]['node_color'] = 'red' if miner.peer_id==num_peers-1 else ('black' if miner.peer_id==num_peers-2 else 'blue')
            chainGraph1.nodes[node]['attribute'] = 0

    # print(chainGraph1.nodes(data=True))
    node_colors1 = [node_data['node_color'] for node, node_data in chainGraph1.nodes(data=True)]
    node_labels1 = {node: node_data['attribute'] for node, node_data in chainGraph1.nodes(data=True)}

    # Assuming you have another graph stored in chainGraph2
    # for node in chainGraph2.nodes():
    #     if 'node_color' not in chainGraph2.nodes[node]:
    #         miner=allBlocks[node].miner
    #         chainGraph2.nodes[node]['node_color'] = 'red' if miner.peer_id==num_peers-1 else ('black' if miner.peer_id==num_peers-2 else 'blue')
    #         chainGraph2.nodes[node]['attribute'] = 0

    # node_colors2 = [node_data['node_color'] for node, node_data in chainGraph2.nodes(data=True)]
    # node_labels2 = {node: node_data['attribute'] for node, node_data in chainGraph2.nodes(data=True)}

    # Create subplots
    # fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # # Plot the first graph
    # ax1 = axes[0]
    plt.figure()
    pos1 = nx.kamada_kawai_layout(chainGraph1)
    nx.draw(chainGraph1, pos1, with_labels=False, labels=node_labels1, arrows=True, node_color=node_colors1)
    # ax1.set_title('Graph 1')

    # # Plot the second graph
    # ax2 = axes[1]
    # pos2 = nx.kamada_kawai_layout(chainGraph2)
    # nx.draw(chainGraph2, pos2, ax=ax2, with_labels=False, labels=node_labels2, arrows=True, node_color=node_colors2)
    # ax2.set_title('Graph 2')

    # plt.tight_layout()
    plt.savefig("two_graphs.png")
    plt.show()
    # break

        
