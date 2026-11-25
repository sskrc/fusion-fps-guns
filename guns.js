// Every gun on the site. `page` = a dedicated interactive page; otherwise the gun opens in viewer.html?g=<id> using `glb`.
export const SECTIONS = [
  { id: 'ra', title: 'ROGUEARENA', ja: 'RogueArena 武器セット', note: '架空のFPS向けにデザインした11丁。どれもリロードや発砲などのアニメーションを再生できます。' },
  { id: 'morph', title: 'MORPH', ja: '変形する銃', note: '形態を切り替えると外装や砲身が組み替わる、架空のエネルギー銃です。' },
  { id: 'classic', title: 'PISTOL', ja: '実銃風ピストル', note: 'マガジンの着脱、発砲、分解まで操作できます。' },
  { id: 'proto', title: 'PROTOTYPES', ja: '初期の3丁', note: '最初に作った未来的な銃。可動部はありません。' },
];

const ra = (id, name, ja, desc) => ({ id, sec: 'ra', name, ja, desc, glb: `./models/RogueArena/${id}/${id}.glb`, thumb: `./assets/thumbs/${id}.jpg` });
const proto = (id, name, ja, desc) => ({ id, sec: 'proto', name, ja, desc, glb: `./models/${id}/${id}.glb`, thumb: `./assets/thumbs/${id}.jpg` });

export const GUNS = [
  ra('RA01_Sidearm', 'RA01 SIDEARM', '標準ハンドガン', 'ストライカー式のポリマーフレーム拳銃。スライド、マガジン、トリガーが動きます。'),
  ra('RA02_BurstPistol', 'RA02 BURST PISTOL', 'バーストハンドガン', '長いスライドと延長マガジンを持つ3点バースト拳銃。セレクターとハンマーも動きます。'),
  ra('RA03_Revolver', 'RA03 REVOLVER', '大型ハンドガン', '銃身がシリンダーの最下段に並ぶ大型リボルバー。シリンダーが上へ振り出します。'),
  ra('RA04_PDW', 'RA04 PDW', '高速SMG', 'グリップ内にマガジンを収めた小型SMG。伸縮ストックと折りたたみフォアグリップ付き。'),
  ra('RA05_EnergySMG', 'RA05 ENERGY SMG', 'エネルギーSMG', '箱形の本体にエネルギーセルを挿すSMG。ストックは右側面へ折りたためます。'),
  ra('RA06_BurstRifle', 'RA06 BURST RIFLE', 'バーストライフル', '光学サイト一体のキャリーハンドルを持つ3点バーストライフル。'),
  ra('RA07_AssaultRifle', 'RA07 ASSAULT RIFLE', 'アサルトライフル', '背の高い一体型レシーバーと全長レールのカービン。ストックとサイトが動きます。'),
  ra('RA08_Shotgun', 'RA08 SHOTGUN', 'ショットガン', '放熱カバーと太いポンプを持つ戦闘用ショットガン。ストックは上へ折りたためます。'),
  ra('RA09_Sniper', 'RA09 SNIPER', 'スナイパーライフル', '全長1.4mの対物ライフル。発砲で銃身が後退し、二脚を展開できます。'),
  ra('RA10_LMG', 'RA10 LMG', '軽機関銃', '横開きの給弾カバーと弾薬ポーチを持つ軽量機関銃。二脚とストックが動きます。'),
  ra('RA11_EnergyLMG', 'RA11 ENERGY LMG', 'エネルギーLMG', 'セルをグリップ後方に挿すブルパップ型。過熱すると側面の冷却フラップが開きます。'),
  { id: 'ORBIS', sec: 'morph', name: 'ORBIS-V', ja: '有機的な変形エミッター', desc: '外装が割れて組み替わる3形態。チャージして発射できます。', page: './orbis.html', thumb: './assets/thumbs/ORBIS.jpg' },
  { id: 'TALOS', sec: 'morph', name: 'TALOS-IX', ja: '機械的な変形レール銃', desc: '歯車とピストンを露出させた3形態。砲身が伸び、二脚とストックが展開します。', page: './talos.html', thumb: './assets/thumbs/TALOS.jpg' },
  { id: 'P230', sec: 'classic', name: 'P230', ja: '小型ピストル', desc: 'マガジンを抜く、撃つ、スライドを引く、分解する、まで操作できる展示ページ。', page: './p230.html', thumb: './assets/thumbs/P230.jpg' },
  proto('SMG_VX9_Wasp', 'VX-9 WASP', 'サブマシンガン', '最初に作った未来的なSMG。'),
  proto('Shotgun_HR12_Breaker', 'HR-12 BREAKER', 'ショットガン', '最初に作った未来的なショットガン。'),
  proto('Sniper_LRX_Longshot', 'LR-X LONGSHOT', 'スナイパーライフル', '最初に作った未来的なスナイパーライフル。'),
];

export const hrefOf = g => g.page || `./viewer.html?g=${g.id}`;
