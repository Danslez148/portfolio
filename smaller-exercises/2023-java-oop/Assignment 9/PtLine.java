class PtLine extends VectorObject {
   private int x1;
   private int y1;
   
   public PtLine(int id, int x, int y, int x1, int y1) {
      super(id, x, y);
      this.x1 = x1;
      this.y1 = y1;
   }
   
   public void draw(char[][] matrix) {
      int ys;
      boolean steep = Math.abs(y1 - y) > Math.abs(x1 - x);
      if (steep) {
         int temp = x;
         x = y;
         y = temp;
         temp = x1;
         x1 = y1;
         y1 = temp;
      }
      if (x > x1) {
         int temp = x;
         x = x1;
         x1 = temp;
         temp = y;
         y = y1;
         y1 = temp;
      }
      if (y < y1) {
         ys = 1;
      } else {
         ys = -1;
      }
      double m = Math.abs(y1 - y) / (x1 - x);
      int j = y;
      double error = 0;
      for (int i = x; i <= x1; i++) {
         if (steep) {
            matrix[i][j] = '*';
         } else {
            matrix[j][i] = '*';
         }
         error = error + m;
         if (error > 0.5) {
            j += ys;
            error--;
         }
      }
   }
}