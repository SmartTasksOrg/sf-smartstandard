<?php
/* SmartStandard - native PHP port. Reproduces sf_smartstandard.core. No deps. */
$IDS = ['STD-README', 'STD-SMARTJSON', 'STD-LICENSE', 'STD-TESTS'];

function std_hash(array $IDS): string {
    return 'sha256:' . substr(hash('sha256', implode(',', $IDS)), 0, 12);
}
function conformance(string $root, array $IDS): array {
    $checks = [
        'STD-README'   => file_exists("$root/README.md"),
        'STD-SMARTJSON' => file_exists("$root/.smart.json"),
        'STD-LICENSE'  => file_exists("$root/LICENSE"),
        'STD-TESTS'    => is_dir("$root/tests"),
    ];
    $drift = []; $present = 0;
    foreach ($IDS as $id) { if ($checks[$id]) $present++; else $drift[] = $id; }
    return ['score' => (int) round(100 * $present / count($IDS)), 'drift' => $drift];
}

$vpath = $argv[1] ?? __DIR__ . '/../conformance/vectors.json';
$vdir = dirname(realpath($vpath));
$v = json_decode(file_get_contents($vpath), true);
$results = [];
foreach ($v['cases'] as $c) {
    if (($c['op'] ?? 'standard') === 'standard') {
        $results[] = ['name' => $c['name'], 'id' => 'iaiso-baseline', 'hash' => std_hash($IDS), 'rules' => $IDS];
    } else {
        $root = $c['root'];
        if ($root[0] !== '/' && !preg_match('/^[A-Za-z]:/', $root)) $root = "$vdir/$root";
        $results[] = array_merge(['name' => $c['name']], conformance($root, $IDS));
    }
}
echo json_encode(['results' => $results], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), "\n";
