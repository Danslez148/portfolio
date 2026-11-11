package csassignment1;

import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class GenericsBST {
    private BSTNode root;
    private boolean created;
    /**
     * Says whether any information has been loaded.
     * @return 
     */
    public boolean isCreated() {
        return created;
    }
    /**
     * Creates an empty binary search tree.
     */
    public GenericsBST() {
        this.root = null;
    }
    /**
     * Creates a binary search from the input of a file to serve as our knowledge base. It does so by created a BSTNode object for every entry of data and adding each to a binary search tree.
     * @param fileName 
     */
    public GenericsBST(String fileName) {
        try {
            Scanner s = new Scanner(new File(fileName));
            while (s.hasNextLine()) {
                this.insert(s.nextLine());              
            }
            this.created = true;
        } catch (IOException e) {
            this.created = false;
        }
    }
    /**
     * Searches for a given term in the data structure.
     * @param s
     * @return 
     */
    public BSTNode findTerm(String s) {
        if (root == null)
            return null;
        else
            return findTerm(s, root);
    }
    /**
     * The second method involved in searching for a given term in the data structure. Essential for recursion.
     * @param s
     * @param n
     * @return 
     */
    public BSTNode findTerm(String s, BSTNode n) {
        int pos = s.compareTo(n.getTerm());
        if (pos == 0)
            return n;
        else if (pos < 0)
            return (n.left == null) ? null : findTerm(s, n.left);
        else
            return (n.right == null) ? null : findTerm(s, n.right);
    }
    /**
     * Inserts a given entry into the data structure.
     * @param s 
     */
    public void insert(String s) {
        if (root == null)
            root = new BSTNode(s);
        else
            insert(s, root);
    }
    /**
     * The second method involved in inserting a given term in the data structure. Essential for recursion.
     * @param s
     * @param n 
     */
    public void insert(String s, BSTNode n) {
        if (s.compareTo(n.data) <= 0) {
            if (n.left == null)
                n.left = new BSTNode(s);
            else
                insert(s, n.left);
        } else {
            if (n.right == null)
                n.right = new BSTNode(s);
            else
                insert(s, n.right);
        }
    }
}
