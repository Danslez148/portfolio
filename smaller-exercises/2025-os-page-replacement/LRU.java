import java.util.Scanner;
import java.util.Stack;
//
public class LRU {



    private static int leastRecentlyUsed(final Memory frames, final Integer[] pageReferences) {
        int pageFaults = 0;
        

    
        int[] lastIndex = new int[frames.size()];
    
        
        outer: for (int i=0; i<pageReferences.length; i++){
        if (frames.contains(pageReferences[i])){
            int a=frames.indexOf(pageReferences[i]);
            lastIndex[a]=i;
            System.out.println("" + pageReferences[i] + ": -");
            continue;
        }
        for (int k=0; k<frames.size(); k++){
            if (frames.isEmpty(k)){
               frames.put(k, pageReferences[i]);
               pageFaults++;
               lastIndex[k]=i;
               System.out.println("" + pageReferences[i] + ": "+ frames.toString());
               continue outer;
            }
        }
        int big = Integer.MAX_VALUE;
        int bigIndex = 0;
        
        for (int j=0; j<lastIndex.length; j++){
            System.out.println("big: " + bigIndex + "  j  " + j);
            System.out.println(lastIndex.length);
            if (lastIndex[j]<big) {
               big=lastIndex[j];
               
               bigIndex=j;
            }
        }
        pageFaults++;
        frames.put(bigIndex, pageReferences[i]);
        lastIndex[bigIndex] = i;
        System.out.println("" + pageReferences[i] + ": " + frames.toString());
        
        }
        return pageFaults;
    }


    public static void main(final String[] args) {
        final Scanner stdIn = new Scanner(System.in);

        System.out.println("Enter the physical memory size (number of frames):");
        final int numFrames = stdIn.nextInt();
        stdIn.nextLine();

        System.out.println("Enter the string of page references:");
        final String referenceString = stdIn.nextLine();

        System.out.printf("Page faults: %d.\n", leastRecentlyUsed(new Memory(numFrames), toArray(referenceString)));
    }

    private static Integer[] toArray(final String referenceString) {
        final Integer[] result = new Integer[referenceString.length()];
        
        for(int i=0; i < referenceString.length(); i++) {
            result[i] = Character.digit(referenceString.charAt(i), 10);
        }
        return result;
    }
}