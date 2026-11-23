# 2. Sourcing

> Generated from the CAD and BOM data (counts are taken from the model, not typed). Numbers marked [estimate] are modelled or unverified; everything else is counted from the model or read from a seller's page.

One chassis, two power levels. The **kit** tiers are every part except the radio, motor, ESC, servo, battery and charger
(bring your own: the minimum spec is in [3. Assembly](03_assembly.md#bring-your-own-electronics)). The **complete** tiers
add the electronics this car was designed and tested on. The 50 mph tier is the same car, motor and ESC on a smaller 2S
pack: moving to 80 mph later costs one 3S pack.

Sellers are US or China/Hong Kong only. Prices were read from the seller's page on the date in the CSV note; [snippet]
means the page blocked reading and the price is from a search listing. Prices move: check before you order.

## 50 mph kit (no electronics)

Modelled: 55.6<!--D:50k_mph=55.6--> mph mid case, 55.4<!--D:50k_mph_hi=55.4--> mph high-drag, 48<!--D:50k_runway=48--> m of runway to 90 % of top speed, 17.2<!--D:50k_amps=17.2--> A at top speed [estimate: speed model + CFD drag band]. **Total 433.13<!--D:50k_usd=433.13--> USD** (real parts 175.01<!--D:50k_real=175.01--> USD; 7.79<!--D:50k_usd_mph=7.79--> USD per mph). File: `bom/bom_50k.csv`.

| Category | Part | Qty | Line USD | Buy |
|---|---|---|---|---|
| consumable | LiPo safety bag 185 x 75 x 60 mm (BuddyRC): cut as the pack's fire barrier | 1.0 | 4.98 | [link](https://www.buddyrc.com/products/fireproof-explosionproof-lipo-battery-safe-bag-lipo-battery-guard-185x75x60mm) |
| consumable | Hook-and-loop battery straps 250 x 20 mm, metal buckle, 3 pcs (BuddyRC) | 1.0 | 4.99 | [link](https://www.buddyrc.com/products/buddyrc-battery-strap) |
| consumable | CA glue for rubber tyres, 25 g (Tamiya 54511): tyre-to-rim beads | 1.0 | 11.0 | [link](https://www.rcjaz.com/product_info.php?products_id=90061169) |
| filament | Filament: Inland PETG-CF (5 % CF), 1 kg (557 g used) | 1 | 34.99 | [link](https://www.microcenter.com/product/687104/inland-175mm-petg-cf-3d-printer-filament-1-kg-(22-lbs)-spool-black) |
| filament | Filament: PETG, 1 kg (404 g used: body panels, wing, tray) | 1 | 16.99 | [link](https://us.store.bambulab.com/products/petg-basic) |
| filament | Filament: TPU 95A (21 g used: bumper, pads) | 1 | 25.19 | [link](https://us.store.bambulab.com/products/tpu-95a-hf) |
| hardware | M3 12.9 socket-cap assortment kit | 1.0 | 14.49 | [link](https://www.aliexpress.us/item/3256812587357446.html) |
| hardware | N52 10x3 mm disc magnets, 10-pack | 1.0 | 9.35 | [link](https://www.aliexpress.us/item/3256810618890302.html) |
| hardware | Drive pins 2 x 10 mm steel, 10-pack (Arrowmax AM-13FB2010) | 1.0 | 2.78 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13FB2010) |
| hardware | M3 hard-fibre washers 3.2 x 7 x 0.5 mm, 100-pack (McMaster-Carr 95225A315): motor thermal break | 1.0 | 16.22 | [link](https://www.mcmaster.com/95225A315) |
| hardware | M4 nyloc nuts, flanged, 4-pack (Jazrider M4-LNF-R; wheel nuts) | 2.0 | 3.8 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=M4-LNF-R) |
| hardware | 5 mm shoulder screw, 30 mm shoulder, M4 thread (McMaster 92981A055) as the fixed layshaft axle | 1.0 | 3.9 | [link](https://www.mcmaster.com/92981A055/) |
| hardware | M3 hex nuts DIN 934, class 8 zinc steel, 100-pack (Albany County Fasteners 5602-022-002) | 2 | 6.0 | [link](https://www.albanycountyfasteners.com/metric-finished-hex-nuts-zinc-plated-class-8-steel-m3-x-05-5602-022-002/) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 6, steel, 10-pack (Arrowmax AM-13CS3006): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3006) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 10, steel, 10-pack (Arrowmax AM-13CS3010): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3010) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 12, steel, 10-pack (Arrowmax AM-13CS3012): 4 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3012) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 16, steel, 10-pack (Arrowmax AM-13CS3016): 8 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3016) |
| hardware | M3 nyloc nuts, steel, 10 pcs (Yokomo ZC-N3LA): 4 used, lower-arm hinges | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=ZC-N3LA) |
| hardware | M3 x 8 self-tapping screws, titanium button-head hex, 10 pcs (3Racing TS-BSM308S): 3 used, spur to drum | 1.0 | 3.1 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=TS-BSM308S) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 2.0 mm, 10 pcs (RAD-AC-10008): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10008) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 1.0 mm, 10 pcs (RAD-AC-10006): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10006) |
| hardware | M4 flat washers DIN 125, 4.3 x 8.8 x 0.8 mm, 304 stainless, 50-pack (Protosupplies): 1 used, layshaft axle | 1.0 | 1.25 | [link](https://protosupplies.com/product/m4-flat-washer-ss-50-pack/) |
| hardware | M3 flat washers 3.2 x 7.0 x 0.5 mm (DIN 125 size), A2 stainless, 100-pack (Albany County Fasteners 5620022) | 1 | 2.0 | [link](https://www.albanycountyfasteners.com/Flat-Washers-A2-Stainless-Steel-p/5620000.htm) |
| hardware | M3 x 12 socket-cap screws, 12.9 black-oxide steel, 100-pack (Zoro Select M07000.030.0012): 34 used, GT-2 body seams + carrier columns | 1 | 6.65 | [link](https://www.zoro.com/zoro-select-m3-050-socket-head-cap-screw-black-oxide-steel-12-mm-length-100-pk-m070000300012/i/G2341586) |
| real: drivetrain | 48P pinion 33T, 7075 hard (Arrowmax AM-348033) | 1.0 | 5.61 | [link](https://www.rcjaz.com/arrowmax-am348033-pinion-gear-48p-33t-7075-hard-p-90082701.html) |
| real: drivetrain | Thread-locker gel for the pinion grub screw (Tamiya 54032) | 1.0 | 6.5 | [link](https://www.rcjaz.com/tamiya-54032-anaerobic-gel-thread-lock-op1032-for-rc-cars-p-90000246.html) |
| real: suspension + drivetrain | 38T belt gear differential with bearing 'for 3Racing Sakura XI' (aftermarket, in stock) | 2.0 | 13.32 | [link](https://www.aliexpress.us/item/3256808911273543.html) |
| real: suspension + drivetrain | Molded 48P 66T spur (Race Opt RO-SG4866, POM) on a printed hub | 1.0 | 5.5 | [link](https://www.rcjaz.com/race-opt-48p-spur-gear-66t-pom-rosg4866-p-9141.html) |
| real: suspension + drivetrain | CVD driveshafts 44 mm 'SAK-X27' type, 2 shafts + 2 bearings per pack (unbranded, in stock) | 2.0 | 25.96 | [link](https://www.ebay.com/itm/265399438971) |
| real: suspension + drivetrain | 4.8 mm STEEL ball studs L6, 10-pack (3Racing 3RAC-BS4806S) | 1.0 | 3.8 | [link](https://www.rcjaz.com/product_info.php?products_id=90057854) |
| real: suspension + drivetrain | 1/10 touring 55 mm aluminium oil shocks, 4-pack (TT-02 type; 55/46 mm hole-to-hole, 9 mm stroke) | 1.0 | 12.67 | [link](https://www.aliexpress.us/item/3256808347555750.html) |
| real: suspension + drivetrain | Compression springs Century Spring 71891, x5 (4 + a spare): OD 16.76, ID 13.59, wire 1.59, 22.35 mm long, 37 lbf/in = 6.48 N/mm | 5.0 | 43.25 | [link](https://www.mwcomponents.com/shop/71891cs) |
| real: suspension + drivetrain | 3Racing 3 mm S3M belts: SAK-A577 S3M423-3 (141T) front + SAK-A576 S3M279-3 (93T) rear | 1.0 | 11.2 | [link](https://www.rcjaz.com/3racing-saka577-sakura-advance-21-front-drive-belt-p-26166.html) |
| real: suspension + drivetrain | Bearings MR105-2RS 5x10x4, 10-pack (3Racing) | 1.0 | 6.2 | [link](https://www.rcjaz.com/double-rubber-seals-bearing-10-mm-pcs-3rbmr1052rs10-p-90002041.html) |
| real: suspension + drivetrain | Bearings MR105-ZZ 5x10x4 metal shields, 10-pack (3Racing 3RB-MR105-ZZ/10): layshaft pair + spares | 1.0 | 6.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=3RB-MR105-ZZ) |
| real: suspension + drivetrain | Bearings 6700ZZ 10x15x4: two 2-packs (3Racing), diff bearings | 1.0 | 3.4 | [link](https://www.rcjaz.com/doublemetalshieldbearing10x15x4mm10pcs3rb6700zz10--p-90002021.html) |
| real: tyres | Tamiya 54994 Reinforced Racing Tires Soft 24 mm (2 pcs, cloth-belted, no foams) | 2.0 | 26.2 | [link](https://www.rcjaz.com/tamiya-54994-tire-reinforced-racing-soft-24mm-pcs-op1994-p-24105.html) |
| real: tyres | Team Powers 1:10 touring tire insert, 40 deg, 4 pcs (TP-TTI4-40OR) | 1.0 | 5.4 | [link](https://www.rcjaz.com/product_info.php?products_id=90057832) |
| shipping | Shipping allowance (rcjaz, AliExpress, Zeee, eBay, McMaster-Carr, BuddyRC, MW Components) | 1.0 | 54.11 | - |
## 50 mph complete

Modelled: 55.6<!--D:50c_mph=55.6--> mph mid case, 55.4<!--D:50c_mph_hi=55.4--> mph high-drag, 48<!--D:50c_runway=48--> m of runway to 90 % of top speed, 17.2<!--D:50c_amps=17.2--> A at top speed [estimate: speed model + CFD drag band]. **Total 612.98<!--D:50c_usd=612.98--> USD** (real parts 344.36<!--D:50c_real=344.36--> USD; 11.02<!--D:50c_usd_mph=11.02--> USD per mph). File: `bom/bom_50c.csv`.

| Category | Part | Qty | Line USD | Buy |
|---|---|---|---|---|
| consumable | LiPo safety bag 185 x 75 x 60 mm (BuddyRC): cut as the pack's fire barrier | 1.0 | 4.98 | [link](https://www.buddyrc.com/products/fireproof-explosionproof-lipo-battery-safe-bag-lipo-battery-guard-185x75x60mm) |
| consumable | Hook-and-loop battery straps 250 x 20 mm, metal buckle, 3 pcs (BuddyRC) | 1.0 | 4.99 | [link](https://www.buddyrc.com/products/buddyrc-battery-strap) |
| consumable | CA glue for rubber tyres, 25 g (Tamiya 54511): tyre-to-rim beads | 1.0 | 11.0 | [link](https://www.rcjaz.com/product_info.php?products_id=90061169) |
| consumable | 4 AA cells for the transmitter | 1 | 4.0 | - |
| filament | Filament: Inland PETG-CF (5 % CF), 1 kg (557 g used) | 1 | 34.99 | [link](https://www.microcenter.com/product/687104/inland-175mm-petg-cf-3d-printer-filament-1-kg-(22-lbs)-spool-black) |
| filament | Filament: PETG, 1 kg (404 g used: body panels, wing, tray) | 1 | 16.99 | [link](https://us.store.bambulab.com/products/petg-basic) |
| filament | Filament: TPU 95A (21 g used: bumper, pads) | 1 | 25.19 | [link](https://us.store.bambulab.com/products/tpu-95a-hf) |
| hardware | M3 12.9 socket-cap assortment kit | 1.0 | 14.49 | [link](https://www.aliexpress.us/item/3256812587357446.html) |
| hardware | N52 10x3 mm disc magnets, 10-pack | 1.0 | 9.35 | [link](https://www.aliexpress.us/item/3256810618890302.html) |
| hardware | Drive pins 2 x 10 mm steel, 10-pack (Arrowmax AM-13FB2010) | 1.0 | 2.78 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13FB2010) |
| hardware | M3 hard-fibre washers 3.2 x 7 x 0.5 mm, 100-pack (McMaster-Carr 95225A315): motor thermal break | 1.0 | 16.22 | [link](https://www.mcmaster.com/95225A315) |
| hardware | M4 nyloc nuts, flanged, 4-pack (Jazrider M4-LNF-R; wheel nuts) | 2.0 | 3.8 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=M4-LNF-R) |
| hardware | 5 mm shoulder screw, 30 mm shoulder, M4 thread (McMaster 92981A055) as the fixed layshaft axle | 1.0 | 3.9 | [link](https://www.mcmaster.com/92981A055/) |
| hardware | M3 hex nuts DIN 934, class 8 zinc steel, 100-pack (Albany County Fasteners 5602-022-002) | 2 | 6.0 | [link](https://www.albanycountyfasteners.com/metric-finished-hex-nuts-zinc-plated-class-8-steel-m3-x-05-5602-022-002/) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 6, steel, 10-pack (Arrowmax AM-13CS3006): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3006) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 10, steel, 10-pack (Arrowmax AM-13CS3010): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3010) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 12, steel, 10-pack (Arrowmax AM-13CS3012): 4 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3012) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 16, steel, 10-pack (Arrowmax AM-13CS3016): 8 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3016) |
| hardware | M3 nyloc nuts, steel, 10 pcs (Yokomo ZC-N3LA): 4 used, lower-arm hinges | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=ZC-N3LA) |
| hardware | M3 x 8 self-tapping screws, titanium button-head hex, 10 pcs (3Racing TS-BSM308S): 3 used, spur to drum | 1.0 | 3.1 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=TS-BSM308S) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 2.0 mm, 10 pcs (RAD-AC-10008): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10008) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 1.0 mm, 10 pcs (RAD-AC-10006): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10006) |
| hardware | M4 flat washers DIN 125, 4.3 x 8.8 x 0.8 mm, 304 stainless, 50-pack (Protosupplies): 1 used, layshaft axle | 1.0 | 1.25 | [link](https://protosupplies.com/product/m4-flat-washer-ss-50-pack/) |
| hardware | M3 flat washers 3.2 x 7.0 x 0.5 mm (DIN 125 size), A2 stainless, 100-pack (Albany County Fasteners 5620022) | 1 | 2.0 | [link](https://www.albanycountyfasteners.com/Flat-Washers-A2-Stainless-Steel-p/5620000.htm) |
| hardware | M3 x 12 socket-cap screws, 12.9 black-oxide steel, 100-pack (Zoro Select M07000.030.0012): 34 used, GT-2 body seams + carrier columns | 1 | 6.65 | [link](https://www.zoro.com/zoro-select-m3-050-socket-head-cap-screw-black-oxide-steel-12-mm-length-100-pk-m070000300012/i/G2341586) |
| real: drivetrain | 48P pinion 33T, 7075 hard (Arrowmax AM-348033) | 1.0 | 5.61 | [link](https://www.rcjaz.com/arrowmax-am348033-pinion-gear-48p-33t-7075-hard-p-90082701.html) |
| real: drivetrain | Thread-locker gel for the pinion grub screw (Tamiya 54032) | 1.0 | 6.5 | [link](https://www.rcjaz.com/tamiya-54032-anaerobic-gel-thread-lock-op1032-for-rc-cars-p-90000246.html) |
| real: electronics | DS3218MG 20 kg metal-gear servo (180 deg) | 1.0 | 14.99 | [link](https://www.aliexpress.us/item/3256808561278747.html) |
| real: electronics | Surpass Hobby 3650 3900KV + 60A ESC combo | 1.0 | 49.09 | [link](https://www.aliexpress.us/item/3256809463381837.html) |
| real: electronics | Aluminium 540 motor heat sink with twin fans (Jazrider JR-FAN2) | 1.0 | 5.11 | [link](https://www.rcjaz.com/jazrider-rc-aluminium-540-motor-heat-sink-gun-metal-wtwin-cooling-fans-p-90084314.html) |
| real: electronics | XT60-female to T-plug-male charge lead, 1 ft (BuddyRC): charger to the T-plug pack | 1.0 | 2.49 | [link](https://www.buddyrc.com/products/charge-cable-xt60-female-to-ec3-male-adapter-cable) |
| real: electronics | Turnigy 3500mAh 2S 60C LiPo, XT60 (130 x 42 x 18 mm, 168 g) [snippet] | 1 | 13.99 | [link](https://hobbyking.com/en_us/turnigy-3500mah-2s-60c-lipo-pack-w-xt60-connector.html) |
| real: electronics | Radio: DumboRC X6 transmitter + X6FG / P6FG gyro receiver | 1 | 47.69 | [link](https://www.ebay.com/itm/257687587815) |
| real: electronics | Charger: ToolkitRC M4AC, mains powered, XT60, balance charging | 1 | 35.99 | [link](https://www.racedayquads.com/products/toolkitrc-m4ac-30w-2-5a-2-4s-ac-smart-charger-xt60) |
| real: suspension + drivetrain | 38T belt gear differential with bearing 'for 3Racing Sakura XI' (aftermarket, in stock) | 2.0 | 13.32 | [link](https://www.aliexpress.us/item/3256808911273543.html) |
| real: suspension + drivetrain | Molded 48P 66T spur (Race Opt RO-SG4866, POM) on a printed hub | 1.0 | 5.5 | [link](https://www.rcjaz.com/race-opt-48p-spur-gear-66t-pom-rosg4866-p-9141.html) |
| real: suspension + drivetrain | CVD driveshafts 44 mm 'SAK-X27' type, 2 shafts + 2 bearings per pack (unbranded, in stock) | 2.0 | 25.96 | [link](https://www.ebay.com/itm/265399438971) |
| real: suspension + drivetrain | 4.8 mm STEEL ball studs L6, 10-pack (3Racing 3RAC-BS4806S) | 1.0 | 3.8 | [link](https://www.rcjaz.com/product_info.php?products_id=90057854) |
| real: suspension + drivetrain | 1/10 touring 55 mm aluminium oil shocks, 4-pack (TT-02 type; 55/46 mm hole-to-hole, 9 mm stroke) | 1.0 | 12.67 | [link](https://www.aliexpress.us/item/3256808347555750.html) |
| real: suspension + drivetrain | Compression springs Century Spring 71891, x5 (4 + a spare): OD 16.76, ID 13.59, wire 1.59, 22.35 mm long, 37 lbf/in = 6.48 N/mm | 5.0 | 43.25 | [link](https://www.mwcomponents.com/shop/71891cs) |
| real: suspension + drivetrain | 3Racing 3 mm S3M belts: SAK-A577 S3M423-3 (141T) front + SAK-A576 S3M279-3 (93T) rear | 1.0 | 11.2 | [link](https://www.rcjaz.com/3racing-saka577-sakura-advance-21-front-drive-belt-p-26166.html) |
| real: suspension + drivetrain | Bearings MR105-2RS 5x10x4, 10-pack (3Racing) | 1.0 | 6.2 | [link](https://www.rcjaz.com/double-rubber-seals-bearing-10-mm-pcs-3rbmr1052rs10-p-90002041.html) |
| real: suspension + drivetrain | Bearings MR105-ZZ 5x10x4 metal shields, 10-pack (3Racing 3RB-MR105-ZZ/10): layshaft pair + spares | 1.0 | 6.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=3RB-MR105-ZZ) |
| real: suspension + drivetrain | Bearings 6700ZZ 10x15x4: two 2-packs (3Racing), diff bearings | 1.0 | 3.4 | [link](https://www.rcjaz.com/doublemetalshieldbearing10x15x4mm10pcs3rb6700zz10--p-90002021.html) |
| real: tyres | Tamiya 54994 Reinforced Racing Tires Soft 24 mm (2 pcs, cloth-belted, no foams) | 2.0 | 26.2 | [link](https://www.rcjaz.com/tamiya-54994-tire-reinforced-racing-soft-24mm-pcs-op1994-p-24105.html) |
| real: tyres | Team Powers 1:10 touring tire insert, 40 deg, 4 pcs (TP-TTI4-40OR) | 1.0 | 5.4 | [link](https://www.rcjaz.com/product_info.php?products_id=90057832) |
| shipping | Shipping allowance (rcjaz, AliExpress, Zeee, eBay, McMaster-Carr, BuddyRC, MW Components) | 1.0 | 54.11 | - |
| shipping | Shipping, RaceDayQuads parcel (charger, cutters) | 1 | 6.5 | - |
## 80 mph kit (no electronics)

Modelled: 81.5<!--D:80k_mph=81.5--> mph mid case, 81.1<!--D:80k_mph_hi=81.1--> mph high-drag, 107<!--D:80k_runway=107--> m of runway to 90 % of top speed, 31.5<!--D:80k_amps=31.5--> A at top speed [estimate: speed model + CFD drag band]. **Total 433.13<!--D:80k_usd=433.13--> USD** (real parts 175.01<!--D:80k_real=175.01--> USD; 5.31<!--D:80k_usd_mph=5.31--> USD per mph). File: `bom/bom_80k.csv`.

| Category | Part | Qty | Line USD | Buy |
|---|---|---|---|---|
| consumable | LiPo safety bag 185 x 75 x 60 mm (BuddyRC): cut as the pack's fire barrier | 1.0 | 4.98 | [link](https://www.buddyrc.com/products/fireproof-explosionproof-lipo-battery-safe-bag-lipo-battery-guard-185x75x60mm) |
| consumable | Hook-and-loop battery straps 250 x 20 mm, metal buckle, 3 pcs (BuddyRC) | 1.0 | 4.99 | [link](https://www.buddyrc.com/products/buddyrc-battery-strap) |
| consumable | CA glue for rubber tyres, 25 g (Tamiya 54511): tyre-to-rim beads | 1.0 | 11.0 | [link](https://www.rcjaz.com/product_info.php?products_id=90061169) |
| filament | Filament: Inland PETG-CF (5 % CF), 1 kg (557 g used) | 1 | 34.99 | [link](https://www.microcenter.com/product/687104/inland-175mm-petg-cf-3d-printer-filament-1-kg-(22-lbs)-spool-black) |
| filament | Filament: PETG, 1 kg (404 g used: body panels, wing, tray) | 1 | 16.99 | [link](https://us.store.bambulab.com/products/petg-basic) |
| filament | Filament: TPU 95A (21 g used: bumper, pads) | 1 | 25.19 | [link](https://us.store.bambulab.com/products/tpu-95a-hf) |
| hardware | M3 12.9 socket-cap assortment kit | 1.0 | 14.49 | [link](https://www.aliexpress.us/item/3256812587357446.html) |
| hardware | N52 10x3 mm disc magnets, 10-pack | 1.0 | 9.35 | [link](https://www.aliexpress.us/item/3256810618890302.html) |
| hardware | Drive pins 2 x 10 mm steel, 10-pack (Arrowmax AM-13FB2010) | 1.0 | 2.78 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13FB2010) |
| hardware | M3 hard-fibre washers 3.2 x 7 x 0.5 mm, 100-pack (McMaster-Carr 95225A315): motor thermal break | 1.0 | 16.22 | [link](https://www.mcmaster.com/95225A315) |
| hardware | M4 nyloc nuts, flanged, 4-pack (Jazrider M4-LNF-R; wheel nuts) | 2.0 | 3.8 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=M4-LNF-R) |
| hardware | 5 mm shoulder screw, 30 mm shoulder, M4 thread (McMaster 92981A055) as the fixed layshaft axle | 1.0 | 3.9 | [link](https://www.mcmaster.com/92981A055/) |
| hardware | M3 hex nuts DIN 934, class 8 zinc steel, 100-pack (Albany County Fasteners 5602-022-002) | 2 | 6.0 | [link](https://www.albanycountyfasteners.com/metric-finished-hex-nuts-zinc-plated-class-8-steel-m3-x-05-5602-022-002/) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 6, steel, 10-pack (Arrowmax AM-13CS3006): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3006) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 10, steel, 10-pack (Arrowmax AM-13CS3010): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3010) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 12, steel, 10-pack (Arrowmax AM-13CS3012): 4 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3012) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 16, steel, 10-pack (Arrowmax AM-13CS3016): 8 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3016) |
| hardware | M3 nyloc nuts, steel, 10 pcs (Yokomo ZC-N3LA): 4 used, lower-arm hinges | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=ZC-N3LA) |
| hardware | M3 x 8 self-tapping screws, titanium button-head hex, 10 pcs (3Racing TS-BSM308S): 3 used, spur to drum | 1.0 | 3.1 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=TS-BSM308S) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 2.0 mm, 10 pcs (RAD-AC-10008): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10008) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 1.0 mm, 10 pcs (RAD-AC-10006): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10006) |
| hardware | M4 flat washers DIN 125, 4.3 x 8.8 x 0.8 mm, 304 stainless, 50-pack (Protosupplies): 1 used, layshaft axle | 1.0 | 1.25 | [link](https://protosupplies.com/product/m4-flat-washer-ss-50-pack/) |
| hardware | M3 flat washers 3.2 x 7.0 x 0.5 mm (DIN 125 size), A2 stainless, 100-pack (Albany County Fasteners 5620022) | 1 | 2.0 | [link](https://www.albanycountyfasteners.com/Flat-Washers-A2-Stainless-Steel-p/5620000.htm) |
| hardware | M3 x 12 socket-cap screws, 12.9 black-oxide steel, 100-pack (Zoro Select M07000.030.0012): 34 used, GT-2 body seams + carrier columns | 1 | 6.65 | [link](https://www.zoro.com/zoro-select-m3-050-socket-head-cap-screw-black-oxide-steel-12-mm-length-100-pk-m070000300012/i/G2341586) |
| real: drivetrain | 48P pinion 33T, 7075 hard (Arrowmax AM-348033) | 1.0 | 5.61 | [link](https://www.rcjaz.com/arrowmax-am348033-pinion-gear-48p-33t-7075-hard-p-90082701.html) |
| real: drivetrain | Thread-locker gel for the pinion grub screw (Tamiya 54032) | 1.0 | 6.5 | [link](https://www.rcjaz.com/tamiya-54032-anaerobic-gel-thread-lock-op1032-for-rc-cars-p-90000246.html) |
| real: suspension + drivetrain | 38T belt gear differential with bearing 'for 3Racing Sakura XI' (aftermarket, in stock) | 2.0 | 13.32 | [link](https://www.aliexpress.us/item/3256808911273543.html) |
| real: suspension + drivetrain | Molded 48P 66T spur (Race Opt RO-SG4866, POM) on a printed hub | 1.0 | 5.5 | [link](https://www.rcjaz.com/race-opt-48p-spur-gear-66t-pom-rosg4866-p-9141.html) |
| real: suspension + drivetrain | CVD driveshafts 44 mm 'SAK-X27' type, 2 shafts + 2 bearings per pack (unbranded, in stock) | 2.0 | 25.96 | [link](https://www.ebay.com/itm/265399438971) |
| real: suspension + drivetrain | 4.8 mm STEEL ball studs L6, 10-pack (3Racing 3RAC-BS4806S) | 1.0 | 3.8 | [link](https://www.rcjaz.com/product_info.php?products_id=90057854) |
| real: suspension + drivetrain | 1/10 touring 55 mm aluminium oil shocks, 4-pack (TT-02 type; 55/46 mm hole-to-hole, 9 mm stroke) | 1.0 | 12.67 | [link](https://www.aliexpress.us/item/3256808347555750.html) |
| real: suspension + drivetrain | Compression springs Century Spring 71891, x5 (4 + a spare): OD 16.76, ID 13.59, wire 1.59, 22.35 mm long, 37 lbf/in = 6.48 N/mm | 5.0 | 43.25 | [link](https://www.mwcomponents.com/shop/71891cs) |
| real: suspension + drivetrain | 3Racing 3 mm S3M belts: SAK-A577 S3M423-3 (141T) front + SAK-A576 S3M279-3 (93T) rear | 1.0 | 11.2 | [link](https://www.rcjaz.com/3racing-saka577-sakura-advance-21-front-drive-belt-p-26166.html) |
| real: suspension + drivetrain | Bearings MR105-2RS 5x10x4, 10-pack (3Racing) | 1.0 | 6.2 | [link](https://www.rcjaz.com/double-rubber-seals-bearing-10-mm-pcs-3rbmr1052rs10-p-90002041.html) |
| real: suspension + drivetrain | Bearings MR105-ZZ 5x10x4 metal shields, 10-pack (3Racing 3RB-MR105-ZZ/10): layshaft pair + spares | 1.0 | 6.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=3RB-MR105-ZZ) |
| real: suspension + drivetrain | Bearings 6700ZZ 10x15x4: two 2-packs (3Racing), diff bearings | 1.0 | 3.4 | [link](https://www.rcjaz.com/doublemetalshieldbearing10x15x4mm10pcs3rb6700zz10--p-90002021.html) |
| real: tyres | Tamiya 54994 Reinforced Racing Tires Soft 24 mm (2 pcs, cloth-belted, no foams) | 2.0 | 26.2 | [link](https://www.rcjaz.com/tamiya-54994-tire-reinforced-racing-soft-24mm-pcs-op1994-p-24105.html) |
| real: tyres | Team Powers 1:10 touring tire insert, 40 deg, 4 pcs (TP-TTI4-40OR) | 1.0 | 5.4 | [link](https://www.rcjaz.com/product_info.php?products_id=90057832) |
| shipping | Shipping allowance (rcjaz, AliExpress, Zeee, eBay, McMaster-Carr, BuddyRC, MW Components) | 1.0 | 54.11 | - |
## 80 mph complete

Modelled: 81.5<!--D:80c_mph=81.5--> mph mid case, 81.1<!--D:80c_mph_hi=81.1--> mph high-drag, 107<!--D:80c_runway=107--> m of runway to 90 % of top speed, 31.5<!--D:80c_amps=31.5--> A at top speed [estimate: speed model + CFD drag band]. **Total 633.98<!--D:80c_usd=633.98--> USD** (real parts 365.36<!--D:80c_real=365.36--> USD; 7.78<!--D:80c_usd_mph=7.78--> USD per mph). File: `bom/bom_80c.csv`.

| Category | Part | Qty | Line USD | Buy |
|---|---|---|---|---|
| consumable | LiPo safety bag 185 x 75 x 60 mm (BuddyRC): cut as the pack's fire barrier | 1.0 | 4.98 | [link](https://www.buddyrc.com/products/fireproof-explosionproof-lipo-battery-safe-bag-lipo-battery-guard-185x75x60mm) |
| consumable | Hook-and-loop battery straps 250 x 20 mm, metal buckle, 3 pcs (BuddyRC) | 1.0 | 4.99 | [link](https://www.buddyrc.com/products/buddyrc-battery-strap) |
| consumable | CA glue for rubber tyres, 25 g (Tamiya 54511): tyre-to-rim beads | 1.0 | 11.0 | [link](https://www.rcjaz.com/product_info.php?products_id=90061169) |
| consumable | 4 AA cells for the transmitter | 1 | 4.0 | - |
| filament | Filament: Inland PETG-CF (5 % CF), 1 kg (557 g used) | 1 | 34.99 | [link](https://www.microcenter.com/product/687104/inland-175mm-petg-cf-3d-printer-filament-1-kg-(22-lbs)-spool-black) |
| filament | Filament: PETG, 1 kg (404 g used: body panels, wing, tray) | 1 | 16.99 | [link](https://us.store.bambulab.com/products/petg-basic) |
| filament | Filament: TPU 95A (21 g used: bumper, pads) | 1 | 25.19 | [link](https://us.store.bambulab.com/products/tpu-95a-hf) |
| hardware | M3 12.9 socket-cap assortment kit | 1.0 | 14.49 | [link](https://www.aliexpress.us/item/3256812587357446.html) |
| hardware | N52 10x3 mm disc magnets, 10-pack | 1.0 | 9.35 | [link](https://www.aliexpress.us/item/3256810618890302.html) |
| hardware | Drive pins 2 x 10 mm steel, 10-pack (Arrowmax AM-13FB2010) | 1.0 | 2.78 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13FB2010) |
| hardware | M3 hard-fibre washers 3.2 x 7 x 0.5 mm, 100-pack (McMaster-Carr 95225A315): motor thermal break | 1.0 | 16.22 | [link](https://www.mcmaster.com/95225A315) |
| hardware | M4 nyloc nuts, flanged, 4-pack (Jazrider M4-LNF-R; wheel nuts) | 2.0 | 3.8 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=M4-LNF-R) |
| hardware | 5 mm shoulder screw, 30 mm shoulder, M4 thread (McMaster 92981A055) as the fixed layshaft axle | 1.0 | 3.9 | [link](https://www.mcmaster.com/92981A055/) |
| hardware | M3 hex nuts DIN 934, class 8 zinc steel, 100-pack (Albany County Fasteners 5602-022-002) | 2 | 6.0 | [link](https://www.albanycountyfasteners.com/metric-finished-hex-nuts-zinc-plated-class-8-steel-m3-x-05-5602-022-002/) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 6, steel, 10-pack (Arrowmax AM-13CS3006): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3006) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 10, steel, 10-pack (Arrowmax AM-13CS3010): 16 used | 2.0 | 6.38 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3010) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 12, steel, 10-pack (Arrowmax AM-13CS3012): 4 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3012) |
| hardware | M3 flat-head (countersunk) hex socket screws M3 x 16, steel, 10-pack (Arrowmax AM-13CS3016): 8 used | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=AM-13CS3016) |
| hardware | M3 nyloc nuts, steel, 10 pcs (Yokomo ZC-N3LA): 4 used, lower-arm hinges | 1.0 | 3.19 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=ZC-N3LA) |
| hardware | M3 x 8 self-tapping screws, titanium button-head hex, 10 pcs (3Racing TS-BSM308S): 3 used, spur to drum | 1.0 | 3.1 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=TS-BSM308S) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 2.0 mm, 10 pcs (RAD-AC-10008): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10008) |
| hardware | M3 aluminium spacer shims 3 x 5.5 x 1.0 mm, 10 pcs (RAD-AC-10006): shock top-eye stack | 1.0 | 7.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=RAD-AC-10006) |
| hardware | M4 flat washers DIN 125, 4.3 x 8.8 x 0.8 mm, 304 stainless, 50-pack (Protosupplies): 1 used, layshaft axle | 1.0 | 1.25 | [link](https://protosupplies.com/product/m4-flat-washer-ss-50-pack/) |
| hardware | M3 flat washers 3.2 x 7.0 x 0.5 mm (DIN 125 size), A2 stainless, 100-pack (Albany County Fasteners 5620022) | 1 | 2.0 | [link](https://www.albanycountyfasteners.com/Flat-Washers-A2-Stainless-Steel-p/5620000.htm) |
| hardware | M3 x 12 socket-cap screws, 12.9 black-oxide steel, 100-pack (Zoro Select M07000.030.0012): 34 used, GT-2 body seams + carrier columns | 1 | 6.65 | [link](https://www.zoro.com/zoro-select-m3-050-socket-head-cap-screw-black-oxide-steel-12-mm-length-100-pk-m070000300012/i/G2341586) |
| real: drivetrain | 48P pinion 33T, 7075 hard (Arrowmax AM-348033) | 1.0 | 5.61 | [link](https://www.rcjaz.com/arrowmax-am348033-pinion-gear-48p-33t-7075-hard-p-90082701.html) |
| real: drivetrain | Thread-locker gel for the pinion grub screw (Tamiya 54032) | 1.0 | 6.5 | [link](https://www.rcjaz.com/tamiya-54032-anaerobic-gel-thread-lock-op1032-for-rc-cars-p-90000246.html) |
| real: electronics | DS3218MG 20 kg metal-gear servo (180 deg) | 1.0 | 14.99 | [link](https://www.aliexpress.us/item/3256808561278747.html) |
| real: electronics | Surpass Hobby 3650 3900KV + 60A ESC combo | 1.0 | 49.09 | [link](https://www.aliexpress.us/item/3256809463381837.html) |
| real: electronics | Aluminium 540 motor heat sink with twin fans (Jazrider JR-FAN2) | 1.0 | 5.11 | [link](https://www.rcjaz.com/jazrider-rc-aluminium-540-motor-heat-sink-gun-metal-wtwin-cooling-fans-p-90084314.html) |
| real: electronics | Zeee 3S 5200 50C soft case, T-plug (Deans) fitted + a loose spare XT60 | 1.0 | 34.99 | [link](https://zeeebattery.com/products/zeee-3s-lipo-battery-5200mah-11-1v-50c-xt60) |
| real: electronics | XT60-female to T-plug-male charge lead, 1 ft (BuddyRC): charger to the T-plug pack | 1.0 | 2.49 | [link](https://www.buddyrc.com/products/charge-cable-xt60-female-to-ec3-male-adapter-cable) |
| real: electronics | Radio: DumboRC X6 transmitter + X6FG / P6FG gyro receiver | 1 | 47.69 | [link](https://www.ebay.com/itm/257687587815) |
| real: electronics | Charger: ToolkitRC M4AC, mains powered, XT60, balance charging | 1 | 35.99 | [link](https://www.racedayquads.com/products/toolkitrc-m4ac-30w-2-5a-2-4s-ac-smart-charger-xt60) |
| real: suspension + drivetrain | 38T belt gear differential with bearing 'for 3Racing Sakura XI' (aftermarket, in stock) | 2.0 | 13.32 | [link](https://www.aliexpress.us/item/3256808911273543.html) |
| real: suspension + drivetrain | Molded 48P 66T spur (Race Opt RO-SG4866, POM) on a printed hub | 1.0 | 5.5 | [link](https://www.rcjaz.com/race-opt-48p-spur-gear-66t-pom-rosg4866-p-9141.html) |
| real: suspension + drivetrain | CVD driveshafts 44 mm 'SAK-X27' type, 2 shafts + 2 bearings per pack (unbranded, in stock) | 2.0 | 25.96 | [link](https://www.ebay.com/itm/265399438971) |
| real: suspension + drivetrain | 4.8 mm STEEL ball studs L6, 10-pack (3Racing 3RAC-BS4806S) | 1.0 | 3.8 | [link](https://www.rcjaz.com/product_info.php?products_id=90057854) |
| real: suspension + drivetrain | 1/10 touring 55 mm aluminium oil shocks, 4-pack (TT-02 type; 55/46 mm hole-to-hole, 9 mm stroke) | 1.0 | 12.67 | [link](https://www.aliexpress.us/item/3256808347555750.html) |
| real: suspension + drivetrain | Compression springs Century Spring 71891, x5 (4 + a spare): OD 16.76, ID 13.59, wire 1.59, 22.35 mm long, 37 lbf/in = 6.48 N/mm | 5.0 | 43.25 | [link](https://www.mwcomponents.com/shop/71891cs) |
| real: suspension + drivetrain | 3Racing 3 mm S3M belts: SAK-A577 S3M423-3 (141T) front + SAK-A576 S3M279-3 (93T) rear | 1.0 | 11.2 | [link](https://www.rcjaz.com/3racing-saka577-sakura-advance-21-front-drive-belt-p-26166.html) |
| real: suspension + drivetrain | Bearings MR105-2RS 5x10x4, 10-pack (3Racing) | 1.0 | 6.2 | [link](https://www.rcjaz.com/double-rubber-seals-bearing-10-mm-pcs-3rbmr1052rs10-p-90002041.html) |
| real: suspension + drivetrain | Bearings MR105-ZZ 5x10x4 metal shields, 10-pack (3Racing 3RB-MR105-ZZ/10): layshaft pair + spares | 1.0 | 6.0 | [link](https://www.rcjaz.com/advanced_search_result.php?keywords=3RB-MR105-ZZ) |
| real: suspension + drivetrain | Bearings 6700ZZ 10x15x4: two 2-packs (3Racing), diff bearings | 1.0 | 3.4 | [link](https://www.rcjaz.com/doublemetalshieldbearing10x15x4mm10pcs3rb6700zz10--p-90002021.html) |
| real: tyres | Tamiya 54994 Reinforced Racing Tires Soft 24 mm (2 pcs, cloth-belted, no foams) | 2.0 | 26.2 | [link](https://www.rcjaz.com/tamiya-54994-tire-reinforced-racing-soft-24mm-pcs-op1994-p-24105.html) |
| real: tyres | Team Powers 1:10 touring tire insert, 40 deg, 4 pcs (TP-TTI4-40OR) | 1.0 | 5.4 | [link](https://www.rcjaz.com/product_info.php?products_id=90057832) |
| shipping | Shipping allowance (rcjaz, AliExpress, Zeee, eBay, McMaster-Carr, BuddyRC, MW Components) | 1.0 | 54.11 | - |
| shipping | Shipping, RaceDayQuads parcel (charger, cutters) | 1 | 6.5 | - |

## Not in any tier total

- **Body:** nothing extra to buy. The GT-2 body is printed (its filament is in the filament lines above) and its
  34<!--D:gt2_m12=34--> M3 × 12 screws, 2 M3 × 10 screws and 36<!--D:gt2_nuts=36--> hex nuts are in the hardware lines of every tier.
- **Tech pack** (car computer, GPS, current sensor, speed meter): 172.32<!--D:tech_usd=172.32--> USD, `bom/bom_tech_addon.csv`. It also
  runs the launch current limit that protects the belts (see [7. Tuning](07_tuning.md#belt-launch-limit)).
- **Tools** if you have none: 33.99<!--D:tools_usd=33.99--> USD, `bom/bom_tools_list.csv`.
- **Option:**
