
import java.util.Arrays;

public class InPlaceInsert {

    public static void main(String[] args) {
        int[] arr = new int[6]; // capacity of 6
        arr[0] = 10;
        arr[1] = 20;
        arr[2] = 30;
        arr[3] = 40;
        int size = 4; // Currently holds 4 elements

        int elementToInsert = 100;
        int index = 5;

        // Shift elements to the right from the back
        for (int i = size; i > index; i--) {
            arr[i] = arr[i - 1];
        }

        // Place the element
        arr[index] = elementToInsert;
        size++;

        System.out.println(Arrays.toString(arr)); // [10, 20, 99, 30, 40, 0]
    }
}
