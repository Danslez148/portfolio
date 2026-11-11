//Copyright M.M.Kuttel 2024 CSC2002S, UCT
package parallelAbelianSandpile;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

//This class is for the grid for the Abelian Sandpile cellular automaton
public class Grid {
	private int rows, columns;
	private int [][] grid; //grid 
	private int [][] updateGrid;//grid for next time step
   private ForkJoinPool pool = new ForkJoinPool(Runtime.getRuntime().availableProcessors());
    
	public Grid(int w, int h) {
		rows = w+2; //for the "sink" border
		columns = h+2; //for the "sink" border
		grid = new int[this.rows][this.columns];
		updateGrid=new int[this.rows][this.columns];
		/* grid  initialization */
		for(int i=0; i<this.rows; i++ ) {
			for( int j=0; j<this.columns; j++ ) {
				grid[i][j]=0;
				updateGrid[i][j]=0;
			}
		}
	}

	public Grid(int[][] newGrid) {
		this(newGrid.length,newGrid[0].length); //call constructor above
		//don't copy over sink border
		for(int i=1; i<rows-1; i++ ) {
			for( int j=1; j<columns-1; j++ ) {
				this.grid[i][j]=newGrid[i-1][j-1];
			}
		}
		
	}
	public Grid(Grid copyGrid) {
		this(copyGrid.rows,copyGrid.columns); //call constructor above
		/* grid  initialization */
		for(int i=0; i<rows; i++ ) {
			for( int j=0; j<columns; j++ ) {
				this.grid[i][j]=copyGrid.get(i,j);
			}
		}
	}
	
	public int getRows() {
		return rows-2; //less the sink
	}

	public int getColumns() {
		return columns-2;//less the sink
	}


	int get(int i, int j) {
		return this.grid[i][j];
	}

	void setAll(int value) {
		//borders are always 0
		for( int i = 1; i<rows-1; i++ ) {
			for( int j = 1; j<columns-1; j++ ) 			
				grid[i][j]=value;
			}
	}
	

	//for the next timestep - copy updateGrid into grid
	public void nextTimeStep() {
		for(int i=1; i<rows-1; i++ ) {
			for( int j=1; j<columns-1; j++ ) {
				this.grid[i][j]=updateGrid[i][j];
			}
		}
	}
	
	//key method to calculate the next update grod
	/*
   boolean update() {
		boolean change=false;
		//do not update border
		for( int i = 1; i<rows-1; i++ ) {
			for( int j = 1; j<columns-1; j++ ) {
				updateGrid[i][j] = (grid[i][j] % 4) + 
						(grid[i-1][j] / 4) +
						grid[i+1][j] / 4 +
						grid[i][j-1] / 4 + 
						grid[i][j+1] / 4;
				if (grid[i][j]!=updateGrid[i][j]) {  
					change=true;
				}
		}} //end nested for
	if (change) { nextTimeStep();}
	return change;
	}
	*/
   
   public boolean update() {
      ParallelGridTask task = new ParallelGridTask(grid, updateGrid, 1, rows - 1, 1, columns - 1);
      boolean changed = pool.invoke(task);
      nextTimeStep();
      return changed;
   }
	
	
	//display the grid in text format
	void printGrid( ) {
		int i,j;
		//not border is not printed
		System.out.printf("Grid:\n");
		System.out.printf("+");
		for( j=1; j<columns-1; j++ ) System.out.printf("  --");
		System.out.printf("+\n");
		for( i=1; i<rows-1; i++ ) {
			System.out.printf("|");
			for( j=1; j<columns-1; j++ ) {
				if ( grid[i][j] > 0) 
					System.out.printf("%4d", grid[i][j] );
				else
					System.out.printf("    ");
			}
			System.out.printf("|\n");
		}
		System.out.printf("+");
		for( j=1; j<columns-1; j++ ) System.out.printf("  --");
		System.out.printf("+\n\n");
	}
	
	//write grid out as an image
	void gridToImage(String fileName) throws IOException {
        BufferedImage dstImage =
                new BufferedImage(rows, columns, BufferedImage.TYPE_INT_ARGB);
        //integer values from 0 to 255.
        int a=0;
        int g=0;//green
        int b=0;//blue
        int r=0;//red

		for( int i=0; i<rows; i++ ) {
			for( int j=0; j<columns; j++ ) {
			     g=0;//green
			     b=0;//blue
			     r=0;//red

				switch (grid[i][j]) {
					case 0:
		                break;
		            case 1:
		            	g=255;
		                break;
		            case 2:
		                b=255;
		                break;
		            case 3:
		                r = 255;
		                break;
		            default:
		                break;
				
				}
		                // Set destination pixel to mean
		                // Re-assemble destination pixel.
		              int dpixel = (0xff000000)
		                		| (a << 24)
		                        | (r << 16)
		                        | (g<< 8)
		                        | b; 
		              dstImage.setRGB(i, j, dpixel); //write it out

			
			}}
		
        File dstFile = new File(fileName);
        ImageIO.write(dstImage, "png", dstFile);
	}
	
	private static final int Boundary = 4;
   public int processors = Runtime.getRuntime().availableProcessors();   
   public class ParallelGridTask extends RecursiveTask<Boolean>{
      int start1, end1, start2, end2;
      
      public ParallelGridTask(int[][]grid, int[][] updateGrid, int instart1, int inend1, int instart2, int inend2){
         this.start1 = instart1;
         this.end1 = inend1;
         this.start2 = instart2;
         this.end2 = inend2;
      }
      
      protected Boolean compute(){  
         boolean result=false;
         if ((end1-start1)<=Boundary){
            for (int i=start1; i<end1; i++){
               for (int j=start2; j<end2; j++){
                  updateGrid[i][j] = grid[i][j]%4 + grid[i-1][j]/4 + grid[i][j+1]/4 + grid[i+1][j]/4 + grid[i][j-1]/4;
                  if (grid[i][j]!=updateGrid[i][j]) {
                     result=true;
                  }
               }
            }
            return result;
         } else {
            int mid = (start1+end1)/2;
            ParallelGridTask pGrid1 = new ParallelGridTask(grid, updateGrid, start1, mid, start2, end2);
            ParallelGridTask pGrid2 = new ParallelGridTask(grid, updateGrid, mid, end1, start2, end2);
            
            invokeAll(pGrid1, pGrid2);
            boolean change1 = pGrid1.join();
            boolean change2 = pGrid2.join();
            return change1 || change2;
        
         }
      }
   }


}
