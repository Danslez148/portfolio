//DS Assingnment 2
//SCHDAN066
//22 March 2024

package genericskbavlapp;

import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class GenericsKbAVLApp {
    
    public static class AVL {
            
            private Node root;
            public boolean created;
            
            public AVL() {
                this.root = null;
            }
            
            public int height (Node node) {
                if (node != null)
                    return node.height;
                return -1;
            }
            
            public int balanceFactor (Node node) {
                return height (node.r) - height(node.l);
            }
            
            public void fixHeight (Node node) {
                node.height = Math.max(height(node.l), height(node.r)+1);
            }
            
            public Node rotateRight (Node p) {
                Node q = p.l;
                p.l = q.r;
                q.r = p;
                fixHeight(p);
                fixHeight(q);
                return q;
            }
            
            public Node rotateLeft (Node q) {
                Node p = q.r;
                q.r = p.l;
                p.l = q;
                fixHeight(q);
                fixHeight(p);
                return p;
            }
            
            public Node balance (Node p) {
                fixHeight(p);
                if (balanceFactor(p) == 2) {
                    if (balanceFactor(p.r) < 0)
                        p.r = rotateRight(p.r);
                    return rotateLeft(p);
                }
                if (balanceFactor(p) == -2) {
                    if (balanceFactor(p.l) > 0)
                        p.l = rotateLeft(p.l);
                    return rotateRight(p);
                }
                return p;
            }
            
            public void insert (String data) {
                root = insert(data, root);
            }
            
            public Node insert (String data, Node node) {
                if (node == null)
                    return new Node(data);
                if (data.compareTo(node.data) <= 0)
                    node.l = insert(data, node.l);
                else
                    node.r = insert(data, node.r);
                return balance(node);
            }
            
            public String searchTerm(String query) {
                return search(root, query);
            }
            
            private String search(Node node, String query) {
                if (node == null) {
                    return null;
                }
                if (node.data.startsWith(query)) {
                    return node.data;
                }
                if (query.compareTo(node.data) <= 0) {
                    return search(node.l, query);
                } else {
                    return search(node.r, query);
                }
            }
            
            private class Node {
                String data;
                int height;
                Node l, r;
                
                Node (String data) {
                    this.data = data;
                    this.height = 1;
                    this.l = null;
                    this.r = null;
                }
            }        
        }
    
    public static void main(String[] args) {
        AVL ourTree = new AVL();
        try {
            Scanner s = new Scanner(new File("GenericsKb.txt"));
            while (s.hasNextLine())
                ourTree.insert(s.nextLine());              
        } catch (IOException e) {
            System.out.println("Unsuccessful:" + e.getMessage());
        }
        
        String query;
        String result;
        try {
            Scanner s2 = new Scanner(new File("GenericsKB-queries.txt"));
            while (s2.hasNextLine()) {
                query = s2.nextLine().trim();
                result = ourTree.searchTerm(query);
                if (result != null) {
                    System.out.println(result);
                } else {
                    System.out.println("Term not found: " + query);
                }             
            }
        } catch (IOException e) {
            System.out.println("Unsuccessful:" + e.getMessage());
        }
        
    }
    
}
