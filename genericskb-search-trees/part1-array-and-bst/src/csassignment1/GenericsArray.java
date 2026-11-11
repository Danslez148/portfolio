package csassignment1;

import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class GenericsArray {
    private String[] arrData = new String[100000];
    private int count = 0;
    private boolean created = false;
    
    /**
     * Says whether any information has been loaded.
     * @return 
     */
    public boolean isCreated() {
        return created;
    }
    /**
     * Creates an array from the input of a file to serve as our knowledge base.
     * @param fileName 
     */
    public GenericsArray(String fileName) {
        try {
            Scanner s = new Scanner(new File(fileName));
            while (s.hasNextLine()) {
                arrData[count] = s.nextLine();
                count++;
            }
            this.created = true;
        } catch (IOException e) {
            this.created = false;
        }
    }
    /**
     * Updates an entry in the array if it is present and the confidence score of the new entry is higher than the confidence score of the old entry.
     * @param givenTerm
     * @param givenStatement
     * @param givenConfidence
     * @return 
     */
    public boolean UpdateArray(String givenTerm, String givenStatement, double givenConfidence) {
        boolean result = false;
        for (int k = 0; k < count; k++) {
            if (getTerm(arrData[k]).equalsIgnoreCase(givenTerm)) {
                if (givenConfidence >= getConfidence(arrData[k])) {
                    arrData[k] = getTerm(arrData[k]) + '\t' + givenStatement + '\t' + givenConfidence;
                    result = true;
                }        
            }
        }
        return result;
    }
    /**
     * Checks whether the given term is present in the knowledge base.
     * @param searchItem
     * @return 
     */
    public String Search(String searchItem) {
        String result = "Not found";
        for (int k = 0; k < count; k++) {
            if (getTerm(arrData[k]).equalsIgnoreCase(searchItem)) {
                result = getStatement(arrData[k])+ '\t' + getConfidence(arrData[k]);
            }
        }
        return result;
    }
    /**
     * Checks whether the given term statement combination is present in the knowledge base.
     * @param searchItem
     * @param searchStatement
     * @return 
     */
    public String StatementSearch(String searchItem, String searchStatement) {
        String result = "Not found";
        for (int k = 0; k < count; k++) {
            if (getTerm(arrData[k]).equalsIgnoreCase(searchItem)) {
                if (getStatement(arrData[k]).equalsIgnoreCase(searchStatement)) {
                    result = "" + getConfidence(arrData[k]);
                }
            }
        }
        return result;
    }
    /**
     * Returns the term of an entry
     * @param arrEntry
     * @return 
     */
    public String getTerm(String arrEntry) {
        return arrEntry.substring(0, arrEntry.indexOf('\t'));
    }
    /**
     * Returns the statement of an entry.
     * @param arrEntry
     * @return 
     */
    public String getStatement(String arrEntry) {
        return arrEntry.substring(arrEntry.indexOf('\t')+1, arrEntry.lastIndexOf('\t'));
    }
    /**
     * Returns the confidence of an entry.
     * @param arrEntry
     * @return 
     */
    public double getConfidence(String arrEntry) {
        return Double.parseDouble(arrEntry.substring(arrEntry.lastIndexOf('\t')+1));
    }
       
    
}
