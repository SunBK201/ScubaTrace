package samples.java;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Set;
import java.util.Map.Entry;

public class Test {

    int globalVar = 0;

    public static int gcd(int a, int b) {
        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    public static List<Integer> gen(String numStr) {
        List<Integer> permuations = new ArrayList<>();
        permute(numStr, 0, permuations);
        return permuations;
    }

    private static void permute(String numStr, int start, List<Integer> permutations) {
        if (start == numStr.length()) {
            if (!numStr.startsWith("0")) {
                permutations.add(Integer.parseInt(numStr));
            }
        }
        for (int i = start; i < numStr.length(); i++) {
            numStr = swap(numStr, start, i);
            permute(numStr, start + 1, permutations);
            numStr = swap(numStr, start, i);
        }
    }

    private static String swap(String numStr, int i, int j) {
        char[] charArray = numStr.toCharArray();
        char temp = charArray[i];
        charArray[i] = charArray[j];
        charArray[j] = temp;
        return new String(charArray);
    }

    public static int countRearrangedNumbers(String numStr) {
        List<Integer> permuations = gen(numStr);
        Set<Integer> unique = new HashSet<>(permuations);
        int z = Integer.parseInt(numStr);
        unique.remove(z);

        int count = 0;
        for (int y : unique) {
            if (gcd(z, y) != 1) {
                count++;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        LinkedHashMap<String, Integer> testCases = new LinkedHashMap<>();
        testCases.put("123", 1);
        testCases.put("1234", 2);
        testCases.put("12345", 3);
        for (Entry<String, Integer> kv : testCases.entrySet()) {
            String numStr = kv.getKey();
            int expected = kv.getValue();
            System.out.printf("Input: %s, Output: %d, Expected: %d%n", numStr, countRearrangedNumbers(numStr),
                    expected);
        }
        // first key
        String numStr = testCases.keySet().iterator().next();

        Integer a = 1;
        System.out.println(a == Integer.parseInt(numStr));
    }
}