package csassignment1;

import javax.swing.JFrame;

public class GenericsKbBSTApp extends javax.swing.JFrame {
    private GenericsBST ourBST;
    /**
     * Instantiation of this class results in the creation of the main GUI.
     */
    public GenericsKbBSTApp() {
        initComponents();
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    }

    @SuppressWarnings("unchecked")
    /*
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 425, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 304, Short.MAX_VALUE)
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents
    */
    // <editor-fold defaultstate="collapsed" desc="Generated Code">                          
    private void initComponents() {

        pnlMain = new javax.swing.JPanel();
        lblHeading = new java.awt.Label();
        lblLoad = new javax.swing.JLabel();
        lblAdd = new javax.swing.JLabel();
        txtFileName = new java.awt.TextField();
        btnLoad = new java.awt.Button();
        txtTerm = new java.awt.TextField();
        txtStatement = new java.awt.TextField();
        txtConfidence = new java.awt.TextField();
        btnAdd = new java.awt.Button();
        lblLoadStatus = new java.awt.Label();
        lblAddResult = new javax.swing.JLabel();
        lblStatementSearch = new javax.swing.JLabel();
        lblTermSearch = new javax.swing.JLabel();
        txtTermSearch = new java.awt.TextField();
        btnTermSearch = new java.awt.Button();
        txtTerm2Search = new java.awt.TextField();
        txtSeqSearch = new java.awt.TextField();
        btnStatementSearch = new java.awt.Button();
        lblSearchReturn1 = new java.awt.Label();
        lblSearchReturn2 = new java.awt.Label();

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
        setSize(new java.awt.Dimension(600, 600));

        lblHeading.setAlignment(java.awt.Label.CENTER);
        lblHeading.setFont(new java.awt.Font("Dialog", 0, 36)); // NOI18N
        lblHeading.setName("lblHeading"); // NOI18N
        lblHeading.setText("GenericsKB");

        lblLoad.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblLoad.setText("Load a knowledge base from a file");
        lblLoad.setName("lblLoad"); // NOI18N

        lblAdd.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblAdd.setText("Add a new statement to the knowledge base");
        lblAdd.setName("lblAdd"); // NOI18N

        txtFileName.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        txtFileName.setName("txtFileName"); // NOI18N
        txtFileName.setText("(File name)");

        btnLoad.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        btnLoad.setLabel("Load");
        btnLoad.setName("btnLoad"); // NOI18N
        btnLoad.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnLoadActionPerformed(evt);
            }
        });

        txtTerm.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        txtTerm.setName("txtTerm"); // NOI18N
        txtTerm.setText("(Term)");

        txtStatement.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        txtStatement.setName("txtStatement"); // NOI18N
        txtStatement.setText("(Statement)");

        txtConfidence.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        txtConfidence.setName("txtConfidence"); // NOI18N
        txtConfidence.setText("(Confidence)");

        btnAdd.setEnabled(false);
        btnAdd.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        btnAdd.setLabel("Add");
        btnAdd.setName("btnAdd"); // NOI18N
        btnAdd.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddActionPerformed(evt);
            }
        });

        lblLoadStatus.setCursor(new java.awt.Cursor(java.awt.Cursor.DEFAULT_CURSOR));
        lblLoadStatus.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblLoadStatus.setName("lblLoadStatus"); // NOI18N
        
        lblAddResult.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblAddResult.setName("lblAddResult"); // NOI18N

        javax.swing.GroupLayout pnlMainLayout = new javax.swing.GroupLayout(pnlMain);
        pnlMain.setLayout(pnlMainLayout);
        pnlMainLayout.setHorizontalGroup(
            pnlMainLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(lblHeading, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .addGroup(pnlMainLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(pnlMainLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(pnlMainLayout.createSequentialGroup()
                        .addComponent(txtTerm, javax.swing.GroupLayout.PREFERRED_SIZE, 106, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(txtStatement, javax.swing.GroupLayout.PREFERRED_SIZE, 280, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(txtConfidence, javax.swing.GroupLayout.PREFERRED_SIZE, 113, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(btnAdd, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(lblAddResult, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addComponent(lblLoad)
                    .addComponent(lblAdd)
                    .addGroup(pnlMainLayout.createSequentialGroup()
                        .addComponent(txtFileName, javax.swing.GroupLayout.PREFERRED_SIZE, 169, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(btnLoad, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(lblLoadStatus, javax.swing.GroupLayout.PREFERRED_SIZE, 73, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap(60, Short.MAX_VALUE))
        );
        pnlMainLayout.setVerticalGroup(
            pnlMainLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(pnlMainLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(lblHeading, javax.swing.GroupLayout.PREFERRED_SIZE, 52, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(lblLoad)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(pnlMainLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(lblLoadStatus, javax.swing.GroupLayout.DEFAULT_SIZE, 29, Short.MAX_VALUE)
                    .addComponent(txtFileName, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnLoad, javax.swing.GroupLayout.DEFAULT_SIZE, 29, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 21, Short.MAX_VALUE)
                .addComponent(lblAdd)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(pnlMainLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(lblAddResult, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)    
                    .addComponent(btnAdd, javax.swing.GroupLayout.DEFAULT_SIZE, 30, Short.MAX_VALUE)
                    .addComponent(txtConfidence, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(txtStatement, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(txtTerm, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addGap(19, 19, 19))
        );

        lblStatementSearch.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblStatementSearch.setText("Search for an item in the knowledge base by term and sequence");
        lblStatementSearch.setName("lblStatementSearch"); // NOI18N

        lblTermSearch.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblTermSearch.setText("Search for an item in the knowledge base by term");
        lblTermSearch.setName("lblTermSearch"); // NOI18N

        txtTermSearch.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        txtTermSearch.setName("txtTermSearch"); // NOI18N
        txtTermSearch.setText("(Term)");

        btnTermSearch.setEnabled(false);
        btnTermSearch.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        btnTermSearch.setLabel("Term Search");
        btnTermSearch.setName("btnTermSearch"); // NOI18N
        btnTermSearch.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnTermSearchActionPerformed(evt);
            }
        });

        txtTerm2Search.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        txtTerm2Search.setName("txtTerm2Search"); // NOI18N
        txtTerm2Search.setText("(Term)");

        txtSeqSearch.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        txtSeqSearch.setName("txtSeqSearch"); // NOI18N
        txtSeqSearch.setText("(Statement)");

        btnStatementSearch.setEnabled(false);
        btnStatementSearch.setCursor(new java.awt.Cursor(java.awt.Cursor.DEFAULT_CURSOR));
        btnStatementSearch.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        btnStatementSearch.setLabel("Statement Search");
        btnStatementSearch.setName("btnStatementSearch"); // NOI18N
        btnStatementSearch.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnStatementSearchActionPerformed(evt);
            }
        });

        lblSearchReturn1.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblSearchReturn1.setName("lblSearchReturn1"); // NOI18N

        lblSearchReturn2.setFont(new java.awt.Font("Segoe UI", 0, 14)); // NOI18N
        lblSearchReturn2.setName("lblSearchReturn2"); // NOI18N

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(pnlMain, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addGroup(layout.createSequentialGroup()
                        .addGap(16, 16, 16)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(lblTermSearch)
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(txtTermSearch, javax.swing.GroupLayout.PREFERRED_SIZE, 106, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(btnTermSearch, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(lblSearchReturn1, javax.swing.GroupLayout.PREFERRED_SIZE, 251, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addGap(0, 0, Short.MAX_VALUE))
                    .addGroup(layout.createSequentialGroup()
                        .addGap(16, 16, 16)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(lblStatementSearch)
                                .addGap(0, 0, Short.MAX_VALUE))
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(txtTerm2Search, javax.swing.GroupLayout.PREFERRED_SIZE, 106, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(txtSeqSearch, javax.swing.GroupLayout.PREFERRED_SIZE, 280, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(btnStatementSearch, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(lblSearchReturn2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(pnlMain, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(lblTermSearch)
                .addGap(16, 16, 16)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(txtTermSearch, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnTermSearch, javax.swing.GroupLayout.DEFAULT_SIZE, 30, Short.MAX_VALUE)
                    .addComponent(lblSearchReturn1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addGap(18, 18, 18)
                .addComponent(lblStatementSearch)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(lblSearchReturn2, javax.swing.GroupLayout.DEFAULT_SIZE, 31, Short.MAX_VALUE)
                    .addComponent(btnStatementSearch, javax.swing.GroupLayout.DEFAULT_SIZE, 31, Short.MAX_VALUE)
                    .addComponent(txtTerm2Search, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(txtSeqSearch, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addGap(67, 67, 67))
        );

        pack();
    }
    /**
     * Pressing the load button after entering a valid textfile name results in the contents of the text file being added to the knowledge base (BST).
     * @param evt 
     */
    private void btnLoadActionPerformed(java.awt.event.ActionEvent evt) {                                        
        ourBST = new GenericsBST(txtFileName.getText());
        if (ourBST.isCreated() == true) {
            lblLoadStatus.setText("Success!");
            btnAdd.setEnabled(true);
            btnTermSearch.setEnabled(true);
            btnStatementSearch.setEnabled(true);          
        } else {
            lblLoadStatus.setText("");
            btnAdd.setEnabled(false);
            btnTermSearch.setEnabled(false);
            btnStatementSearch.setEnabled(false);
        }
        
    }                                       
    /**
     * Pressing add after entering the sufficient information results in the addition of a new entry into the knowledge base or an existing one being updated.
     * @param evt 
     */
    private void btnAddActionPerformed(java.awt.event.ActionEvent evt) {                                       
        if (ourBST.findTerm(txtTerm.getText()) == null) {
            ourBST.insert(txtTerm.getText() + '\t' + txtStatement.getText() + '\t' + txtConfidence.getText());
            lblAddResult.setText("Added");
        } else if (ourBST.findTerm(txtTerm.getText()).getConfidence() <= Double.parseDouble(txtConfidence.getText())) {
            ourBST.findTerm(txtTerm.getText()).setData(txtTerm.getText() + '\t' + txtStatement.getText() + '\t' + txtConfidence.getText());
            lblAddResult.setText("Updated");
        } else {
            lblAddResult.setText("Not updated");
       }
    }                                      
    /**
     * Searches for the entered term.
     * @param evt 
     */
    private void btnTermSearchActionPerformed(java.awt.event.ActionEvent evt) {                                              
        String result = "";
        BSTNode n = ourBST.findTerm(txtTermSearch.getText());
        if (n == null) {
            result = "Not found";
        } else {
            result = n.getStatement() + '\t' + n.getConfidence();
        }
        lblSearchReturn1.setText(result);
    }                                             
    /**
     * Searches for the combination of the entered term and statement.
     * @param evt 
     */
    private void btnStatementSearchActionPerformed(java.awt.event.ActionEvent evt) {                                                   
        String result = "";
        BSTNode n = ourBST.findTerm(txtTermSearch.getText());
        if (n == null) {
            result = "Not found";
        } else {
            if (n.getStatement().equalsIgnoreCase(txtSeqSearch.getText())) {
                result = "" + n.getConfidence();
            } else {
                result = "Not found";
            }
        }
        lblSearchReturn2.setText(result);
    }
    /**
     * Creates an instance of the class (makes a GUI).
     * @param args 
     */
    public static void main(String args[]) {
        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                new GenericsKbBSTApp().setVisible(true);
            }
        });
    }
    
    private java.awt.Button btnAdd;
    private java.awt.Button btnLoad;
    private java.awt.Button btnStatementSearch;
    private java.awt.Button btnTermSearch;
    private javax.swing.JLabel lblAdd;
    private javax.swing.JLabel lblAddResult;
    private java.awt.Label lblHeading;
    private javax.swing.JLabel lblLoad;
    private java.awt.Label lblLoadStatus;
    private java.awt.Label lblSearchReturn1;
    private java.awt.Label lblSearchReturn2;
    private javax.swing.JLabel lblStatementSearch;
    private javax.swing.JLabel lblTermSearch;
    private javax.swing.JPanel pnlMain;
    private java.awt.TextField txtConfidence;
    private java.awt.TextField txtFileName;
    private java.awt.TextField txtSeqSearch;
    private java.awt.TextField txtStatement;
    private java.awt.TextField txtTerm;
    private java.awt.TextField txtTerm2Search;
    private java.awt.TextField txtTermSearch;
    // Variables declaration - do not modify//GEN-BEGIN:variables
    // End of variables declaration//GEN-END:variables
}
