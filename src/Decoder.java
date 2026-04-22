import javax.sound.sampled.*;
import java.io.File;

public class Decoder {

    public static byte[] readAudio(String filename) throws Exception {
        File file = new File(filename);
        AudioInputStream ais = AudioSystem.getAudioInputStream(file);
        return ais.readAllBytes();
    }

    public static String audioToBinary(byte[] audioData) {

        StringBuilder binary = new StringBuilder();

        int windowSize = 400; 
        int threshold = 1000; 

        boolean inBeep = false;
        int beepLength = 0;

        for (int i = 0; i < audioData.length; i += 2 * windowSize) {

            long sum = 0;

            // read 16-bit samples
            for (int j = i; j < i + 2 * windowSize && j + 1 < audioData.length; j += 2) {

                int sample = (audioData[j + 1] << 8) | (audioData[j] & 0xff);
                sum += Math.abs(sample);
            }

            long avg = sum / windowSize;

            if (avg > threshold) {
                inBeep = true;
                beepLength += windowSize;
            } else {
                if (inBeep) {

                    if (beepLength < 12000) {
                        binary.append("0");
                    } else {
                        binary.append("1");
                    }

                    beepLength = 0;
                    inBeep = false;
                }
            }
        }

        return binary.toString();
    }

    public static String binaryToText(String binary) {
        StringBuilder text = new StringBuilder();

        for (int i = 0; i + 8 <= binary.length(); i += 8) {
            String byteStr = binary.substring(i, i + 8);
            int charCode = Integer.parseInt(byteStr, 2);
            text.append((char) charCode);
        }

        return text.toString();
    }
}