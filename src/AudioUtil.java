import javax.sound.sampled.*;
import java.io.*;

public class AudioUtil {

    private static final float SAMPLE_RATE = 44100;
    private static final int FREQUENCY = 1000;

    // 16-bit tone
    public static byte[] generateTone(int durationMs) {
        int numSamples = (int)((durationMs / 1000.0) * SAMPLE_RATE);
        byte[] data = new byte[numSamples * 2]; // 16-bit = 2 bytes

        for (int i = 0; i < numSamples; i++) {
            double angle = 2.0 * Math.PI * i * FREQUENCY / SAMPLE_RATE;
            short value = (short)(Math.sin(angle) * 32767);

            data[2 * i] = (byte)(value & 0xff);
            data[2 * i + 1] = (byte)((value >> 8) & 0xff);
        }

        return data;
    }

    public static byte[] generateSilence(int durationMs) {
        int numSamples = (int)((durationMs / 1000.0) * SAMPLE_RATE);
        return new byte[numSamples * 2];
    }

    public static void saveWav(byte[] audioData, String filename) throws Exception {
        AudioFormat format = new AudioFormat(SAMPLE_RATE, 16, 1, true, false);

        ByteArrayInputStream bais = new ByteArrayInputStream(audioData);
        AudioInputStream ais = new AudioInputStream(bais, format, audioData.length / 2);

        File file = new File(filename);
        file.getParentFile().mkdirs();

        AudioSystem.write(ais, AudioFileFormat.Type.WAVE, file);
    }
}