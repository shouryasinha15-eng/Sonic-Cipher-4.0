import java.util.Scanner;

public class Main {

    public static void main(String[] args) {

        try {
            if (args.length >= 2) {
                String mode = args[0];
                String filePath = args[1];

                if (mode.equals("ENCODE")) {
                    Scanner sc = new Scanner(System.in);
                    System.out.print("Enter text: ");
                    String text = sc.nextLine();

                    String binary = Encoder.textToBinary(text);
                    System.out.println("Binary: " + binary);

                    byte[] audioData = Encoder.binaryToAudio(binary);
                    AudioUtil.saveWav(audioData, filePath);
                    System.out.println("Audio file generated: " + filePath);

                    // Decode to verify
                    byte[] readData = Decoder.readAudio(filePath);
                    String decodedBinary = Decoder.audioToBinary(readData);
                    System.out.println("Decoded Binary: " + decodedBinary);
                    String decodedText = Decoder.binaryToText(decodedBinary);
                    System.out.println("Decoded Text: " + decodedText);
                } else if (mode.equals("DECODE")) {
                    byte[] readData = Decoder.readAudio(filePath);
                    String decodedBinary = Decoder.audioToBinary(readData);
                    System.out.println("Decoded Binary: " + decodedBinary);
                    String decodedText = Decoder.binaryToText(decodedBinary);
                    System.out.println("Decoded Text: " + decodedText);
                }
            } else {
                Scanner sc = new Scanner(System.in);

                System.out.print("Enter text: ");
                String text = sc.nextLine();

                // Encode
                String binary = Encoder.textToBinary(text);
                System.out.println("Binary: " + binary);

                byte[] audioData = Encoder.binaryToAudio(binary);
                AudioUtil.saveWav(audioData, "output/encoded.wav");

                System.out.println("Audio file generated: output/encoded.wav");

                // Decode
                byte[] readData = Decoder.readAudio("output/encoded.wav");

                String decodedBinary = Decoder.audioToBinary(readData);
                System.out.println("Decoded Binary: " + decodedBinary);

                String decodedText = Decoder.binaryToText(decodedBinary);
                System.out.println("Decoded Text: " + decodedText);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}