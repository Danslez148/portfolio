import java.util.Scanner;
import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;

public class GridMaker
{
    public static void main(String[] args) throws Exception 
    {
        int rows, columns,value;
        String opt;
        Scanner scn = new Scanner(System.in);
        System.out.println("Enter the number of rows");
        rows = Integer.parseInt(scn.nextLine());
        System.out.println("Enter the number of columns");
        columns = Integer.parseInt(scn.nextLine());
        System.out.println("Are all cells one value? (y/n)");
        opt = scn.nextLine();
        System.out.println("Enter the value");
        value = Integer.parseInt(scn.nextLine());
        scn.close();

        int[][] grid = new int[rows][columns];
        String fileName;
        if (opt.equals("n"))
        {
            fileName  = rows + "_by_" + rows +"_centre" + value +".csv";
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < columns; j++)
                {
                    if (i == rows/2 && j == columns/2)
                    {
                        grid[i][j] = value;
                    }
                    else
                    {
                        grid[i][j] = 0;
                    }
                }
            }
        }
        else
        {
            fileName  = rows + "_by_" + rows +"_All_" + value +".csv";
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < columns; j++)
                {
                    grid[i][j] = value;
                }
            }
        }

        File file = new File(fileName);
        BufferedWriter bw = new BufferedWriter(new FileWriter(file, true));
        String header  = rows + "," + columns;
        bw.append(header);
        bw.newLine();
        for (int i = 0; i < rows; i++)
        {
            String line = "";
            for(int j = 0; j < columns; j++)
            {
                if (j < columns-1)
                {
                    line += grid[i][j] + ",";
                }
                else
                {
                    line += grid[i][j];
                }
            }
            bw.append(line);
            if(i < rows -1)
            {
                bw.newLine();
            }
            
        }
        bw.close();
    }
}
