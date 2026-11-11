class VLine extends VectorObject {
   private int Height;
   
   public VLine(int id, int x, int y, int Height) {
      super(id, x, y);
      this.Height = Height;
   }
   
   public void draw(char[][] matrix) {
      int last = y + Height - 1;
      for (int i = y; i <= last; i++) {
         matrix[i][x] = '*';
      }
   }
}