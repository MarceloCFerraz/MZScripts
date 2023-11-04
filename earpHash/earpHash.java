import java.util.Arrays;
import java.util.Base64;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import static java.nio.charset.StandardCharsets.UTF_8;

public class earpHash {
    public static void main(String[] args) {

    // Example args:
    //     name:    "BOARD OF REGENTS"
    //     addr1:   "270 WASHINGTON ST SW"
    //     addr2:   "GUARD TO SIGN IN STE 7096 MAILROOM"
    //     city:    "ATLANTA"
    //     state:   "GA"
    //     zip:     "30334"
    //     country: "US"

        if(args.length == 0) {
            System.out.println("Proper usage is: java earpHash locationName addr1 addr2 city state zip country");
            System.exit(0);
        }

        String myAddr = String.join("", args);
        
        MessageDigest md = null;

        try {

            md = MessageDigest.getInstance("MD5");

        } catch ( NoSuchAlgorithmException e ) {

            e.printStackTrace();

        }

        md.update(myAddr.getBytes(UTF_8));
        String myHash = Base64.getEncoder().encodeToString(md.digest());

        System.out.println(myHash);
    }
}
