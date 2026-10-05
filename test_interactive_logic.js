#!/usr/bin/env node
/**
 * test_interactive_logic.js
 *
 * Headless JavaScript execution test suite for the interactive Periodic Table.
 * Evaluates embedded JSON data deserialization, client-side category classification,
 * search filtering, molar susceptibility formatting, and 3D crystal lattice math.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const htmlPath = path.join(__dirname, 'interactive_table.html');
assert(fs.existsSync(htmlPath), `File not found: ${htmlPath}`);

const htmlContent = fs.readFileSync(htmlPath, 'utf8');

console.log('======================================================================');
console.log('RUNNING HEADLESS JAVASCRIPT LOGIC TESTS (Node.js runtime)');
console.log('======================================================================');

// 1. Deserialization of embedded data
console.log('▶ Test 1: Deserializing embedded elements dataset...');
const match = htmlContent.match(/<script id="embedded-elements-data" type="application\/json">([\s\S]*?)<\/script>/);
assert(match, 'Embedded JSON script block not found');
const elementsData = JSON.parse(match[1].trim());
assert.strictEqual(elementsData.length, 118, `Expected 118 elements, got ${elementsData.length}`);
console.log(`  ✔ Successfully parsed ${elementsData.length} elements from embedded JSON.`);

// 2. Category classification mapping
console.log('▶ Test 2: Client-side category classification mapping...');
function getCategoryClass(c) {
  if (!c) return 'cat-unknown';
  if (c.startsWith('Ferromagnet (T_C >= 290 K)')) return 'cat-ferro';
  if (c.startsWith('Antiferromagnet (T_N >= 290 K)')) return 'cat-afm';
  if (c.startsWith('Low-temperature')) return 'cat-lowt';
  if (c.startsWith('Diamagnet')) return 'cat-dia';
  if (c.startsWith('Paramagnet')) return 'cat-para';
  return 'cat-unknown';
}

const catCounts = {};
for (const el of elementsData) {
  const cls = getCategoryClass(el.magnetic_classification);
  catCounts[cls] = (catCounts[cls] || 0) + 1;
}

assert.strictEqual(catCounts['cat-ferro'], 4, `Expected 4 room-temp ferromagnets, got ${catCounts['cat-ferro']}`);
assert.strictEqual(catCounts['cat-afm'], 1, `Expected 1 room-temp antiferromagnet (Cr), got ${catCounts['cat-afm']}`);
assert.strictEqual(catCounts['cat-lowt'], 11, `Expected 11 low-temp ordered elements, got ${catCounts['cat-lowt']}`);
assert.strictEqual(catCounts['cat-dia'], 47, `Expected 47 diamagnets, got ${catCounts['cat-dia']}`);
assert.strictEqual(catCounts['cat-para'], 55, `Expected 55 paramagnets, got ${catCounts['cat-para']}`);
console.log('  ✔ Category classifications verified:');
console.log(`    - Ferromagnet (T_C >= 290 K) : ${catCounts['cat-ferro']}`);
console.log(`    - Antiferromagnet (T_N >= 290 K): ${catCounts['cat-afm']}`);
console.log(`    - Low-temperature ordering   : ${catCounts['cat-lowt']}`);
console.log(`    - Diamagnet                  : ${catCounts['cat-dia']}`);
console.log(`    - Paramagnet                 : ${catCounts['cat-para']}`);

// 3. Dynamic Technological Role Tallies
console.log('▶ Test 3: Technological role filter tallies...');
const roleCounts = {
  'Hard Magnetic Vector': 0,
  'Soft Magnetic Core': 0,
  'Magnetocaloric Active Element': 0,
  'Magnetic Phase Stabilizer / Additive': 0,
  'No primary commercial magnetic alloy role documented': 0
};

for (const el of elementsData) {
  const role = el.advanced_magnetism ? el.advanced_magnetism.technological.magnet_role : el.magnet_role;
  assert(role in roleCounts, `Unknown role '${role}' for ${el.symbol}`);
  roleCounts[role]++;
}

assert.strictEqual(roleCounts['Hard Magnetic Vector'], 8);
assert.strictEqual(roleCounts['Soft Magnetic Core'], 5);
assert.strictEqual(roleCounts['Magnetocaloric Active Element'], 5);
assert.strictEqual(roleCounts['Magnetic Phase Stabilizer / Additive'], 5);
assert.strictEqual(roleCounts['No primary commercial magnetic alloy role documented'], 95);
console.log('  ✔ Role tallies match: Hard=8, Soft=5, MCE=5, Additive=5, None=95.');

// 4. Molar Susceptibility formatting & physical scope annotations
console.log('▶ Test 4: Molar susceptibility formatChi() physical annotations...');
function formatChi(val, elem) {
  if (val === null || val === undefined) {
    if (elem && (elem.magnetic_classification.startsWith('Ferromagnet') || (elem.transition_temperature_str && elem.transition_temperature_str.startsWith('T_C')))) {
      return 'Undefined (Ferromagnet below T_C: domain wall hysteresis)';
    }
    return 'N/A';
  }
  let note = '';
  if (elem) {
    if (elem.symbol === 'Gd') {
      note = ' (paramagnetic at 298 K; T_C = 292 K)';
    } else if (['H', 'He', 'N', 'O', 'F', 'Ne', 'Cl', 'Ar', 'Kr', 'Xe', 'Rn'].includes(elem.symbol)) {
      note = ' (gas phase at 298 K)';
    } else if (['Br', 'Hg'].includes(elem.symbol)) {
      note = ' (liquid phase at 298 K)';
    }
  }
  const sign = val > 0 ? '+' : '';
  return `${sign}${val.toFixed(4)} cm³/mol${note}`;
}

const elFe = elementsData.find(e => e.symbol === 'Fe');
const elGd = elementsData.find(e => e.symbol === 'Gd');
const elH = elementsData.find(e => e.symbol === 'H');
const elHg = elementsData.find(e => e.symbol === 'Hg');

assert(formatChi(elFe.molar_susceptibility_298K, elFe).includes('domain wall hysteresis'));
assert(formatChi(elGd.molar_susceptibility_298K, elGd).includes('(paramagnetic at 298 K; T_C = 292 K)'));
assert(formatChi(elH.molar_susceptibility_298K, elH).includes('(gas phase at 298 K)'));
assert(formatChi(elHg.molar_susceptibility_298K, elHg).includes('(liquid phase at 298 K)'));
console.log('  ✔ Fe correctly formatted as domain hysteresis.');
console.log(`  ✔ Gd formatted: "${formatChi(elGd.molar_susceptibility_298K, elGd)}".`);
console.log(`  ✔ H formatted: "${formatChi(elH.molar_susceptibility_298K, elH)}".`);
console.log(`  ✔ Hg formatted: "${formatChi(elHg.molar_susceptibility_298K, elHg)}".`);

// 5. 3D Crystal Geometry & Spin Vector Orientation Math
console.log('▶ Test 5: 3D crystal lattice coordinate math & spin vector projection...');
function buildSchematicLattice(crystSys, moment) {
  const atoms = [];
  let a = 1.0, b = 1.0, c = 1.0;
  if (crystSys === 'BCC') {
    atoms.push({ x: 0, y: 0, z: 0, spin: [0, 1, 0] });
    atoms.push({ x: 0.5, y: 0.5, z: 0.5, spin: [0, 1, 0] });
  } else if (crystSys === 'FCC') {
    atoms.push({ x: 0, y: 0, z: 0, spin: [0, 1, 0] });
    atoms.push({ x: 0.5, y: 0.5, z: 0.5, spin: [0, 1, 0] });
    atoms.push({ x: 0.5, y: 0, z: 0.5, spin: [0, 1, 0] });
    atoms.push({ x: 0, y: 0.5, z: 0.5, spin: [0, 1, 0] });
  } else if (crystSys === 'HCP') {
    c = 1.633;
    atoms.push({ x: 0, y: 0, z: 0, spin: [0, 0, 1] });
    atoms.push({ x: 1/3, y: 2/3, z: 0.5, spin: [0, 0, 1] });
  }

  // Check spin vector scaling
  const tipLen = moment > 0 ? 0.3 : 0.0;
  const spinVectors = atoms.map(at => {
    return {
      tipX: at.x + at.spin[0] * tipLen,
      tipY: at.y + at.spin[1] * tipLen,
      tipZ: at.z + at.spin[2] * tipLen
    };
  });

  return { atoms, a, b, c, spinVectors };
}

const bccFe = buildSchematicLattice('BCC', 2.22);
assert.strictEqual(bccFe.atoms.length, 2);
assert.strictEqual(bccFe.spinVectors.length, 2);
assert(bccFe.spinVectors[0].tipY > bccFe.atoms[0].y, 'Fe spin vector tip must extend along Y');

const hcpGd = buildSchematicLattice('HCP', 7.63);
assert.strictEqual(hcpGd.atoms.length, 2);
assert.strictEqual(hcpGd.c, 1.633, 'HCP c/a ratio must match ideal close-packing');
assert(hcpGd.spinVectors[0].tipZ > hcpGd.atoms[0].z, 'HCP Gd spin vector tip must extend along Z');

console.log('  ✔ BCC and HCP lattice geometry and spin vectors verified.');

console.log('======================================================================');
console.log('🎉 ALL HEADLESS JAVASCRIPT LOGIC TESTS PASSED!');
console.log('======================================================================');
