# Complete parking collections

[Back to the README](../README.md)

`locations()` returns a `ParkingLocations` result with `records`, `total_count`, `pages_fetched` and `complete`. Without a limit it retrieves the full selection; with `limit=10` it returns at most ten records. `pages_fetched` excludes the final source verification request.

`complete` indicates that all records reported by the source were received, including a verified empty selection. Inconsistent pages or changing totals raise `ODPAmsterdamError`. This does not guarantee an atomic source snapshot or current parking availability; inspect `regimes` for restrictions.

For complete deliveries, use `await client.parking_collection(parking_type="E6a", max_records=10000)`. It returns the uniform `ParkingCollection` contract:

| Field | Meaning |
| --- | --- |
| `records` | All parsed `ParkingSpot` records in the selection |
| `total_count` | Source-reported selection count |
| `pages_fetched` | Data pages fetched; excludes the final verification request |
| `source_version` | Verified dataset-wide revision, or `None` when unavailable |
| `complete` | Always `True` for a successful result |

`max_records` is a safety bound: exceeding it raises `ODPAmsterdamResultsError`, without returning a truncated result. Existing `locations()` remains available for deliberately limited queries. Each record's `source_attributes` preserves the original API record, including geometry, restrictions and additional fields; no NIPKaart mapping is applied here.

Amsterdam has no verified dataset-wide revision in this API, so `source_version` is `None`. The final count and first-record check catches some changes during pagination, but neither an individual `versiedatum` nor a matching count proves an atomic snapshot. Completeness covers the reported selection, not all physical parking spaces or live availability.
