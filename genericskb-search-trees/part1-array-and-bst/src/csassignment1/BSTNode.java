package csassignment1;

public class BSTNode {
    String data;
    BSTNode left;
    BSTNode right;
    /**
     * Creates a node object that is used to populate the binary search tree and hold information from the knowledge base.
     * @param inData 
     */
    public BSTNode(String inData) {
        this.data = inData;
        this.left = null;
        this.right = null;
    }
    /**
     * Sets the data contained in the node.
     * @param data 
     */
    public void setData(String data) {
        this.data = data;
    }
    /**
     * Returns the term of the entry stored in this node.
     * @return 
     */
    public String getTerm() {
        return data.substring(0, data.indexOf('\t'));
    }
    /**
     * Returns statement stored in this node.
     * @return 
     */
    public String getStatement() {
        return data.substring(data.indexOf('\t')+1, data.lastIndexOf('\t'));
    }
    /**
     * Returns confidence score of the entry in this node.
     * @return 
     */
    public double getConfidence() {
        return Double.parseDouble(data.substring(data.lastIndexOf('\t')+1));
    }
}
