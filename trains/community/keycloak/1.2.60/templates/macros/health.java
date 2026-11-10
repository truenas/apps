{% macro health_check(scheme) -%}
public class HealthCheck {
    public static void main(String[] args) {
        try {
            String healthUrl = "{{ scheme }}://localhost:9000/health";
            java.net.HttpURLConnection conn = (java.net.HttpURLConnection)
                java.net.URI.create(healthUrl).toURL().openConnection();

            // For HTTPS, disable SSL verification (health check only)
            if (conn instanceof javax.net.ssl.HttpsURLConnection) {
                javax.net.ssl.HttpsURLConnection httpsConn = (javax.net.ssl.HttpsURLConnection) conn;

                // Trust all certificates
                javax.net.ssl.TrustManager[] trustAll = new javax.net.ssl.TrustManager[] {
                    new javax.net.ssl.X509TrustManager() {
                        public java.security.cert.X509Certificate[] getAcceptedIssuers() { return null; }
                        public void checkClientTrusted(java.security.cert.X509Certificate[] certs, String authType) { }
                        public void checkServerTrusted(java.security.cert.X509Certificate[] certs, String authType) { }
                    }
                };

                javax.net.ssl.SSLContext sc = javax.net.ssl.SSLContext.getInstance("SSL");
                sc.init(null, trustAll, new java.security.SecureRandom());
                httpsConn.setSSLSocketFactory(sc.getSocketFactory());

                // Disable hostname verification
                httpsConn.setHostnameVerifier((hostname, session) -> true);
            }

            int responseCode = conn.getResponseCode();
            System.exit(responseCode == java.net.HttpURLConnection.HTTP_OK ? 0 : 1);

        } catch (Exception e) {
            // Any exception means unhealthy
            System.exit(1);
        }
    }
}
{%- endmacro %}
