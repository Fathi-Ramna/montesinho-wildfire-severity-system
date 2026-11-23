# ICNF/SGIF source manifest

## Source

- Provider: Instituto da Conservação da Natureza e das Florestas (ICNF), Portugal
- Dataset: individual SGIF rural-fire records
- Official landing page: https://www.icnf.pt/florestas/gfr/gfrgestaoinformacao/estatisticas
- Retrieved: 2026-08-09
- Coverage in the downloaded release: 2001-2025
- Raw national event records: 497,478
- Main-sheet columns: 41

The official landing page divides the current release into three ZIP archives. The archives and extracted workbooks under `data/raw/icnf_sgif/` are source artifacts and must not be edited in place.

## Download inventory

| Coverage | Official URL | Local archive | Bytes | SHA-256 |
|---|---|---|---:|---|
| 2001-2010 | https://www.icnf.pt/api/file/doc/6f1861934bbc866f | `archives/12-Registos-Incendios-SGIF-2001-2010.zip` | 87,206,496 | `D833055032E114D2946CDAE5FC85E0E82FD3EBDDF6A439C883561F530D4F334A` |
| 2011-2020 | https://www.icnf.pt/api/file/doc/c77d0e2c5bb91f1c | `archives/13-Registos-Incendios-SGIF-2011-2020.zip` | 61,954,542 | `0294404B857679038DB4FD97D54DB77CB0DF2DC945DCC74C569BB0CFC9EC4A4F` |
| 2021-2025 | https://www.icnf.pt/api/file/doc/8b2adaf3ea9b42ab | `archives/RegistoIncendiosSGIF-2021-2025.zip` | 14,531,421 | `2080D71B1420638E181A9864BFD142C2C1149F22E30B06815B49E3D16ACB1EFC` |

## Extracted workbook inventory

| Workbook | Event records | Bytes | SHA-256 |
|---|---:|---:|---|
| `extracted/2001_2010/Registos_Incendios_SGIF_2001_2010.xlsx` | 279,743 | 87,206,286 | `145ECCD782825413FA6A350DC30D94F5460B3E5779CE825BE6D5A4B7BAEDEEA2` |
| `extracted/2011_2020/Registos_Incendios_SGIF_2011_2020.xlsx` | 177,129 | 61,954,332 | `3B1BFDC746793001A8D884B67B5FF551FC58BE32F7B801AEB13778CEF62D4C31` |
| `extracted/2021_2025/Registos_Incendios_SGIF_2021_2025.xlsx` | 40,606 | 14,531,211 | `DF0BE8C1BF84BCF17A2512C2A69AFBA5EEEB26488E9D44736A5E5091BDE2B816` |

Each workbook contains a main SGIF event sheet and a `Legenda` sheet. Later releases also include SQL provenance, and the 2021-2025 release contains a cause-code table.

## Why this source is useful

Unlike the legacy UCI table, SGIF supplies stable event identifiers, exact alert dates and times, exact coordinates, component and total burned areas, protected-area labels, FWI-family indices, causes, response timestamps, duration, and alert source.

The released workbooks do **not** include direct temperature, relative humidity, wind, or rainfall measurements. Those variables must be joined from one documented historical weather source before a model equivalent to the current weather-only SVR can be trained.

## Preliminary Montesinho audit

`RNAP` is defined by ICNF as indicating that the ignition point is inside the national protected-area network. A case-insensitive scan found:

- 1,964 rows tagged `Montesinho`/`MONTESINHO` for 2001-2025;
- 1,642 rows tagged to Montesinho for the recommended non-overlap period 2004-2025;
- 1,642 non-null SGIF identifiers and no duplicate identifiers in that preliminary cohort;
- complete alert timestamps, total/component areas, latitude/longitude, and ETRS89 coordinates;
- three rows (0.18%) missing each FWI-family field;
- total area from 0 to 1,057.5 ha, with a median of 1.0 ha;
- 19 zero-area records, 109 records below 0.01 ha, 31 records at or above 100 ha, and five records at or above 500 ha;
- no component-sum discrepancy greater than 0.011 ha.

This is a candidate count, not the final cohort. The `RNAP` tag must be checked against an official Montesinho boundary in EPSG:3763 before modelling. The case difference also needs normalization while preserving the original value.

## Folder contract

```text
data/
|-- raw/icnf_sgif/
|   |-- archives/       # downloaded ZIP files; immutable
|   `-- extracted/      # extracted official XLSX files; immutable
|-- interim/icnf_sgif/  # audited event extracts and join diagnostics
|-- processed/icnf_sgif/# final model-ready tables
`-- reference/icnf_sgif/# source manifest, dictionaries, and boundary metadata

reports/
|-- figures/icnf_sgif/  # expansion-specific figures
`-- tables/icnf_sgif/   # expansion-specific audit and model tables
```

## Reuse caution

The official statistics page provides public downloads, but an explicit standard reuse license was not displayed with these workbooks during retrieval. Attribute ICNF/SGIF, retain this manifest, and clarify redistribution terms before publishing or repackaging raw event coordinates.

## Official Montesinho boundary

- Provider: ICNF RNAP geospatial service
- Layer: `BDG/RNAP/MapServer/0` (`RNAP - Limites`)
- Feature: `Montesinho`, code `PNM`
- Classification: `Parque Natural`
- Reported area: 74,224.89 ha
- CRS: PT-TM06/ETRS89 (`EPSG:3763`)
- Service layer: https://sigservices.icnf.pt/server/rest/services/BDG/RNAP/MapServer/0
- Retrieved: 2026-08-09

| Reference file | Bytes | SHA-256 |
|---|---:|---|
| `montesinho_boundary/montesinho_boundary_epsg3763.geojson` | 158,827 | `425F488DD55ECD1EA14EB932294D93BEB347FD0C7F315F34683185FDD4636D18` |
| `montesinho_boundary/icnf_rnap_layer_metadata.json` | 5,817 | `06E2013F21C278F00CD3D50EA139C049442926E158F1E26334D444B3FA1B14A1` |
| `montesinho_boundary/icnf_geodata_use_conditions.pdf` | 582,950 | `443F9F6101E703424AC3250C9D3E75DC7C397E20D65BC9CC6DD3548C0E09C9D0` |

The GeoJSON query requested the geometry in EPSG:3763 so it can be compared directly with the SGIF `X_ETRS89` and `Y_ETRS89` ignition-point coordinates without reprojection.
