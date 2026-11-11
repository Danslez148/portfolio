class HLine extends VectorObject {
   private int Length;
   
   public HLine(int id, int x, int y, int Length) {
      super(id, x, y);
      this.Length = Length;
   }
   
   public void draw(char[][] matrix) {
      int last = x + Length - 1;
      for (int i = x; i <= last; i++) {
         matrix[y][i] = '*';
      }
   }
}