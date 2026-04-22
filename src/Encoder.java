import java.io.ByteArrayOutputStream;

public class Encoder {

    public static String textToBinary(String text) {
        StringBuilder binary = new StringBuilder();

        for (char c : text.toCharArray()) {
            String bin = String.format("%8s", Integer.toBinaryString(c))
                    .replace(' ', '0');
            binary.append(bin);
        }

        return binary.toString();
    }

    public static byte[] binaryToAudio(String binary) throws Exception {
        ByteArrayOutputStream output = new ByteArrayOutputStream();

        for (char bit : binary.toCharArray()) {

            if (bit == '0') {
                output.write(AudioUtil.generateTone(200)); // for every 0 after the
                                                           // Binary conversion 200ms beep
            } else if (bit == '1') {
                output.write(AudioUtil.generateTone(500)); // for every 1 after the
                                                           // Binary conversion 500ms beep
            }

            // gap between bits
            output.write(AudioUtil.generateSilence(50));
        }

        return output.toByteArray();
    }
}