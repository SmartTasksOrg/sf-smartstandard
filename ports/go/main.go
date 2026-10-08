// SmartStandard - native Go port. Reproduces sf_smartstandard.core.standard()/conformance().
// Standard library only.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"strings"
)

var IDS = []string{"STD-README", "STD-SMARTJSON", "STD-LICENSE", "STD-TESTS"}

func standardHash() string {
	s := sha256.Sum256([]byte(strings.Join(IDS, ",")))
	return "sha256:" + hex.EncodeToString(s[:])[:12]
}
func exists(p string) bool { _, e := os.Stat(p); return e == nil }
func isdir(p string) bool  { fi, e := os.Stat(p); return e == nil && fi.IsDir() }

func conformance(root string) (int, []string) {
	checks := map[string]bool{
		"STD-README":   exists(filepath.Join(root, "README.md")),
		"STD-SMARTJSON": exists(filepath.Join(root, ".smart.json")),
		"STD-LICENSE":  exists(filepath.Join(root, "LICENSE")),
		"STD-TESTS":    isdir(filepath.Join(root, "tests")),
	}
	drift := []string{}
	present := 0
	for _, id := range IDS {
		if checks[id] {
			present++
		} else {
			drift = append(drift, id)
		}
	}
	score := int(math.Round(100 * float64(present) / float64(len(IDS))))
	return score, drift
}

func main() {
	vpath := filepath.Join("..", "conformance", "vectors.json")
	if len(os.Args) > 1 {
		vpath = os.Args[1]
	}
	abs, _ := filepath.Abs(vpath)
	vdir := filepath.Dir(abs)
	raw, _ := os.ReadFile(vpath)
	var v struct {
		Cases []map[string]interface{} `json:"cases"`
	}
	json.Unmarshal(raw, &v)
	results := []interface{}{}
	for _, c := range v.Cases {
		name, _ := c["name"].(string)
		op, _ := c["op"].(string)
		if op == "" || op == "standard" {
			results = append(results, map[string]interface{}{
				"name": name, "id": "iaiso-baseline", "hash": standardHash(), "rules": IDS})
		} else {
			root, _ := c["root"].(string)
			if !filepath.IsAbs(root) {
				root = filepath.Join(vdir, root)
			}
			score, drift := conformance(root)
			results = append(results, map[string]interface{}{
				"name": name, "score": score, "drift": drift})
		}
	}
	b, _ := json.MarshalIndent(map[string]interface{}{"results": results}, "", "  ")
	fmt.Println(string(b))
}
