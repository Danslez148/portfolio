import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.PriorityQueue;
import java.util.Scanner;

public class SimulatorOne {
    static class GraphException extends RuntimeException {
	private static final long serialVersionUID = 1L;

	public GraphException( String name ) {
            super( name );
        }
    }
    
    static class Edge {
        public Vertex destination;   // Second vertex in Edge
        public int weight;   // Edge cost
    
        public Edge(Vertex d, int w) {
            destination = d;
            weight = w;
        }
    }
    
    static class Path implements Comparable<Path>{
        public Vertex destination;
        public int weight;
        
        public Path(Vertex d, int w) {
            destination = d;
            weight = w;
        }
        
        public int compareTo(Path rhs) {
            int otherWeight = rhs.weight;
            return weight < otherWeight ? -1 : weight > otherWeight ? 1 : 0;
        }
    }
    
    static class Vertex {
        public String name;
        public List<Edge> adj;
        public double dist;   // Cost
        public Vertex prev;   // Previous vertex on shortest path
        public int scratch;   // Extra variable used in algorithm
        public int numShortestSolutions;
        
        public Vertex( String nm ) {
            name = nm;
            adj = new LinkedList<Edge>( );
            reset( );
        }
        
        public void reset() {
            dist = Graph.INFINITY;
            prev = null;
            scratch = 0;
            numShortestSolutions = 0;
        }
    }
    
    static class Graph {
        public static final double INFINITY = Double.MAX_VALUE;
        private Map<String,Vertex> vertexMap = new HashMap<String,Vertex>();
        
        public void addEdge(String sourceName, String destName, int weight) {
            Vertex v = getVertex(sourceName);
            Vertex w = getVertex(destName);
            v.adj.add(new Edge(w, weight));
        }
        
        public String printPath(String destName) {
            Vertex w = vertexMap.get(destName);
            if(w == null)
                throw new NoSuchElementException( "Destination vertex not found" );
            else if(w.dist == INFINITY)
                return destName + " is unreachable";
            else {
                //System.out.print("(Cost is: " + w.dist + ") ");
                
                int numShortestSolutions = w.numShortestSolutions;
                if (numShortestSolutions > 1) {
                    return "multiple solutions cost " + (int) Math.round(w.dist);
                } else {
                    return printPath(w);
                }
                              
                
 //this               return printPath(w);
 //               System.out.println();
            }
        }
        
        private String printPath(Vertex dest) {
            String result = "";
            if(dest.prev != null) {
                result += printPath(dest.prev);
                //System.out.print(" to ");
                result += " ";
            }
            result += dest.name;
            return result;
        }
        
        private Vertex getVertex(String vertexName) {
            Vertex v = vertexMap.get(vertexName);
            if(v == null) {
                v = new Vertex( vertexName );
                vertexMap.put( vertexName, v );
            }
            return v;
        }
        
        private void clearAll() {
            for(Vertex v : vertexMap.values())
                v.reset();
        }
        
        private int numShortestSolutions = 1;
        
        public void dijkstra(String startName) {
            PriorityQueue<Path> pq = new PriorityQueue<Path>();
            
            double minCost = INFINITY;
            
//            System.out.println(startName);
            
            Vertex start = vertexMap.get(startName);
            
            if( start == null )
                throw new NoSuchElementException("Start vertex not found");

            clearAll( );
            pq.add(new Path(start, 0));
            start.dist = 0;
        
            int nodesSeen = 0;
            while(!pq.isEmpty() && nodesSeen < vertexMap.size())
        {
            Path vrec = pq.remove();
            Vertex v = vrec.destination;
            if( v.scratch != 0 )  // already processed v
                continue;
                
            v.scratch = 1;
            nodesSeen++;

                for( Edge e : v.adj ) {
                    Vertex w = e.destination;
                    int cvw = e.weight;
                
                    if( cvw < 0 )
                        throw new GraphException( "Graph has negative edges" );
                    
                    if( w.dist > v.dist + cvw )
                    {
                        w.dist = v.dist +cvw;
                        w.prev = v;
                        pq.add( new Path(w, (int) Math.round(w.dist)));
                        
                        if (w.dist < minCost) {
                            minCost = w.dist;
                            w.numShortestSolutions = 1;
                        } else if (w.dist == minCost) {
                            w.numShortestSolutions++;
                        }                       
                    } else if (w.dist == v.dist + cvw) {
                       w.numShortestSolutions++; 
                    }
                }
            }
        }
    }
    
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        
        Graph g = new Graph();
        
        int numNodes = Integer.parseInt(s.nextLine());
        
        for (int i = 0; i < numNodes; i++) {
            String[] nodeLine = s.nextLine().split(" ");
            String name = nodeLine[0];
            
            for (int j = 1; j < nodeLine.length; j+=2) {
            
                int destination = Integer.parseInt(nodeLine[j]);
                int weight = Integer.parseInt(nodeLine[j+1]);
                g.addEdge(name, String.valueOf(destination), weight);
                
 //this               g.addEdge(name, nodeLine[j], Integer.parseInt(nodeLine[j+1]));
            }
        }
        
        int numShops = Integer.parseInt(s.nextLine());
        String[] shopNodes = s.nextLine().split(" ");
        
        int numClients = Integer.parseInt(s.nextLine());
        String[] clientNodes = s.nextLine().split(" ");
        
        for (int i = 0; i < numClients; i++) {
            System.out.println("client " + clientNodes[i]);
            
            List<String> closestTaxis = new ArrayList<>();
            List<String> taxiRoutes = new ArrayList<>();
            double closestDistance = Graph.INFINITY;
            
            for (String taxi:shopNodes) {
                g.dijkstra(taxi);              
                double distance = g.vertexMap.get(clientNodes[i]).dist;
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestTaxis.clear();
                    taxiRoutes.clear();
                    closestTaxis.add(taxi);
                    taxiRoutes.add(g.printPath(clientNodes[i]));
                } else if ((distance == closestDistance) && (distance != Graph.INFINITY)) {
                    closestTaxis.add(taxi);
                    taxiRoutes.add(g.printPath(clientNodes[i]));
                }
            }
            
            List<String> closestShops = new ArrayList<>();
            List<String> shopRoutes = new ArrayList<>();
            double closestDistanceToShop = Graph.INFINITY;
            
            for (String shop : shopNodes) {
                g.dijkstra(clientNodes[i]);
                double distanceToShop = g.vertexMap.get(shop).dist;
                if (distanceToShop < closestDistanceToShop){
                        closestDistanceToShop = distanceToShop;
                        closestShops.clear();
                        shopRoutes.clear();
                        closestShops.add(shop);
                        shopRoutes.add(g.printPath(shop));
                    } else if ((distanceToShop == closestDistanceToShop) && (distanceToShop != Graph.INFINITY)) {
                        closestShops.add(shop);
                        shopRoutes.add(g.printPath(shop));
                    }

            }
            if (!closestShops.isEmpty() && !closestTaxis.isEmpty()) {
                for (int j = 0; j < closestTaxis.size(); j++) {
                    System.out.println("taxi " + closestTaxis.get(j));
                    g.dijkstra(closestTaxis.get(j));
                    String pathResult = g.printPath(clientNodes[i]);
                    System.out.println(pathResult);
                    
 //this                   System.out.println(taxiRoutes.get(j));
                }
                for (int k = 0; k < closestShops.size(); k++) {
                    System.out.println("shop " + closestShops.get(k));
                    g.dijkstra(clientNodes[i]);
                    String pathResult2 = g.printPath(closestShops.get(k));
                    System.out.println(pathResult2); 
                    
 //this                   System.out.println(shopRoutes.get(k));
                }
            } else {
                System.out.println("cannot be helped");
            }
            
        }                       
    } 
} 
            