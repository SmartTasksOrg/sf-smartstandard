import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/*
 * SmartStandard - native Java port. Reproduces sf_smartstandard.core.standard()/conformance().
 * JDK-only.  javac SmartStandard.java && java SmartStandard [vectors.json]
 */
public class SmartStandard {

    static final String[] IDS = {"STD-README", "STD-SMARTJSON", "STD-LICENSE", "STD-TESTS"};

    static String standardHash() throws Exception {
        byte[] d = MessageDigest.getInstance("SHA-256").digest(String.join(",", IDS).getBytes("UTF-8"));
        StringBuilder b = new StringBuilder();
        for (byte x : d) b.append(String.format("%02x", x));
        return "sha256:" + b.substring(0, 12);
    }

    static Map<String, Object> conformance(Path root) {
        Map<String, Boolean> checks = new LinkedHashMap<>();
        checks.put("STD-README", Files.exists(root.resolve("README.md")));
        checks.put("STD-SMARTJSON", Files.exists(root.resolve(".smart.json")));
        checks.put("STD-LICENSE", Files.exists(root.resolve("LICENSE")));
        checks.put("STD-TESTS", Files.isDirectory(root.resolve("tests")));
        List<String> drift = new ArrayList<>();
        int present = 0;
        for (String id : IDS) { if (checks.get(id)) present++; else drift.add(id); }
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("score", (int) Math.round(100.0 * present / IDS.length));
        m.put("drift", drift);
        return m;
    }

    static String esc(String s) {
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) switch (c) {
            case '"' -> b.append("\\\""); case '\\' -> b.append("\\\\");
            case '\n' -> b.append("\\n"); case '\r' -> b.append("\\r"); case '\t' -> b.append("\\t");
            default -> b.append(c);
        }
        return b.toString();
    }

    @SuppressWarnings("unchecked")
    static String toJson(Object o) {
        if (o == null) return "null";
        if (o instanceof String s) return "\"" + esc(s) + "\"";
        if (o instanceof Boolean || o instanceof Integer || o instanceof Long) return o.toString();
        if (o instanceof String[] a) return toJson(Arrays.asList(a));
        if (o instanceof List<?> l) {
            StringBuilder b = new StringBuilder("[");
            for (int i = 0; i < l.size(); i++) { if (i > 0) b.append(","); b.append(toJson(l.get(i))); }
            return b.append("]").toString();
        }
        Map<String, Object> m = (Map<String, Object>) o;
        StringBuilder b = new StringBuilder("{"); boolean f = true;
        for (var e : m.entrySet()) { if (!f) b.append(","); f = false;
            b.append("\"").append(esc(e.getKey())).append("\":").append(toJson(e.getValue())); }
        return b.append("}").toString();
    }

    public static void main(String[] args) throws Exception {
        String vpath = args.length >= 1 ? args[0]
            : Paths.get(System.getProperty("user.dir"), "..", "conformance", "vectors.json").toString();
        Path vdir = Paths.get(vpath).toAbsolutePath().getParent();
        Json j = new Json(Files.readString(Paths.get(vpath)));
        Map<String, Object> root = j.parseObject();
        @SuppressWarnings("unchecked")
        List<Object> cases = (List<Object>) root.get("cases");
        List<Object> results = new ArrayList<>();
        for (Object oc : cases) {
            @SuppressWarnings("unchecked")
            Map<String, Object> c = (Map<String, Object>) oc;
            String name = (String) c.get("name");
            String op = (String) c.getOrDefault("op", "standard");
            Map<String, Object> out = new LinkedHashMap<>();
            out.put("name", name);
            if (op.equals("standard")) {
                out.put("id", "iaiso-baseline");
                out.put("hash", standardHash());
                out.put("rules", Arrays.asList(IDS));
            } else {
                String r = (String) c.get("root");
                Path root2 = Paths.get(r).isAbsolute() ? Paths.get(r) : vdir.resolve(r);
                out.putAll(conformance(root2));
            }
            results.add(out);
        }
        Map<String, Object> top = new LinkedHashMap<>();
        top.put("results", results);
        System.out.println(toJson(top));
    }

    static class Json {
        final String s; int i;
        Json(String s) { this.s = s; }
        void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }
        Map<String, Object> parseObject() { ws(); return (Map<String, Object>) value(); }
        Object value() { ws(); char c = s.charAt(i);
            return switch (c) { case '{' -> obj(); case '[' -> arr(); case '"' -> str();
                case 't', 'f' -> bool(); case 'n' -> nul(); default -> num(); }; }
        Map<String, Object> obj() { Map<String, Object> m = new LinkedHashMap<>(); i++; ws();
            if (s.charAt(i) == '}') { i++; return m; }
            while (true) { ws(); String k = str(); ws(); i++; m.put(k, value()); ws();
                if (s.charAt(i) == ',') { i++; continue; } i++; break; } return m; }
        List<Object> arr() { List<Object> a = new ArrayList<>(); i++; ws();
            if (s.charAt(i) == ']') { i++; return a; }
            while (true) { a.add(value()); ws(); if (s.charAt(i) == ',') { i++; continue; } i++; break; } return a; }
        String str() { StringBuilder b = new StringBuilder(); i++;
            while (true) { char c = s.charAt(i++); if (c == '"') break;
                if (c == '\\') { char e = s.charAt(i++); switch (e) {
                    case '"' -> b.append('"'); case '\\' -> b.append('\\'); case '/' -> b.append('/');
                    case 'n' -> b.append('\n'); case 'r' -> b.append('\r'); case 't' -> b.append('\t');
                    case 'b' -> b.append('\b'); case 'f' -> b.append('\f');
                    case 'u' -> { b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; }
                    default -> b.append(e); } } else b.append(c); }
            return b.toString(); }
        Object bool() { if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; } i += 5; return Boolean.FALSE; }
        Object nul() { i += 4; return null; }
        Object num() { int st = i; while (i < s.length() && "+-.eE0123456789".indexOf(s.charAt(i)) >= 0) i++;
            return Double.parseDouble(s.substring(st, i)); }
    }
}
