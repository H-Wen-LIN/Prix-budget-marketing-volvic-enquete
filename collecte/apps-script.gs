/**
 * Collecte des réponses du questionnaire (Google Apps Script lié à une Google Sheet).
 * Installation : voir collecte/INSTALLATION.md.
 *
 * - doPost : reçoit une réponse (JSON envoyé par index.html) et l'ajoute comme une ligne de l'onglet « Reponses ».
 *   Une réponse déjà reçue (même id) n'est jamais écrite deux fois : le navigateur peut donc renvoyer sans risque.
 * - doGet : simple test de disponibilité ({ ok: true, reponses: <nombre> }), sans exposer les données.
 *   Avec ?export=csv&key=<clé>, renvoie toutes les réponses en CSV, uniquement si la clé correspond
 *   à la propriété de script EXPORT_KEY (Paramètres du projet > Propriétés du script).
 * Aucune donnée nominative n'est attendue ni stockée.
 */
var SHEET_NAME = 'Reponses';
var COLUMNS = ['id', 'recu_le', 'version', 'statut', 'debut', 'fin', 'consentement', 'F1', 'F2', 'F3',
  'C1', 'controle_ok', 'groupe_controle', 'P1', 'P2', 'P3', 'P4',
  'G_3.50', 'G_2.90', 'G_2.40', 'G_1.90', 'G_1.50', 'GG_prix_accepte',
  'bien_etre', 'routine', 'valeurs', 'innovation', 'confiance', 'qualite', 'rse',
  'genre', 'regime', 'depense_50cl'];

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(COLUMNS);
    sh.setFrozenRows(1);
  }
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    var data = JSON.parse(e.postData.contents);
    var id = String(data.id || '');
    if (!/^[a-z0-9]{6,40}$/.test(id)) return json_({ ok: false, error: 'id invalide' });
    lock.waitLock(20000);
    var sh = sheet_();
    var last = sh.getLastRow();
    if (last > 1) {
      var found = sh.getRange(2, 1, last - 1, 1).createTextFinder(id).matchEntireCell(true).findNext();
      if (found) return json_({ ok: true, id: id, duplicate: true });
    }
    data.recu_le = new Date().toISOString();
    data.groupe_controle = data.controle_ok === 1 ? 'Bonne réponse contrôle'
      : data.controle_ok === 0 ? 'Erreur contrôle' : 'Non atteint';
    var row = COLUMNS.map(function (c) {
      var v = data[c];
      if (v === undefined || v === null) return '';
      if (typeof v === 'number' || typeof v === 'boolean') return v;
      var s = String(v).slice(0, 200);
      return /^[=+\-@]/.test(s) ? "'" + s : s; // évite qu'un texte soit interprété comme une formule
    });
    sh.appendRow(row);
    return json_({ ok: true, id: id, duplicate: false });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (ignore) {}
  }
}

function doGet(e) {
  var sh = sheet_();
  var p = (e && e.parameter) || {};
  if (p.export === 'csv') {
    // Export of all responses, only with the secret key stored in Project Settings > Script properties (EXPORT_KEY).
    var key = PropertiesService.getScriptProperties().getProperty('EXPORT_KEY');
    if (!key || p.key !== key) return json_({ ok: false });
    var values = sh.getDataRange().getValues();
    var csv = values.map(function (row) {
      return row.map(function (v) {
        if (v instanceof Date) v = v.toISOString();
        var s = String(v);
        return /[;"\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
      }).join(';');
    }).join('\n');
    return ContentService.createTextOutput(csv).setMimeType(ContentService.MimeType.CSV);
  }
  return json_({ ok: true, reponses: Math.max(sh.getLastRow() - 1, 0) });
}
