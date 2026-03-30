from CONSTANTS import BUCKET_ORDER, NUM_BUCKETS

def impart_workflow_pid_to_kdamonds(pid, region_count = 2 * NUM_BUCKETS):
    string = """
{
    "kdamonds": [
        {
            "refresh_ms": 0,
            "contexts": [
                {
                    "ops": "vaddr",
                    "targets": [
                        {
                            "pid": """ + str(pid) + """,
                            "obsolete": false,
                            "regions": [
                                {
                                    "start": "0",
                                    "end": "281,474,976,710,656"
                                }
                            ]
                        }
                    ],
                    "intervals": {
                        "sample_us": "1 ms",
                        "aggr_us": "100 ms",
                        "ops_update_us": "1 s",
                        "intervals_goal": {
                            "access_bp": "0 %",
                            "aggrs": "0",
                            "min_sample_us": "0 ns",
                            "max_sample_us": "0 ns"
                        }
                    },
                    "nr_regions": {
                        "min": "512",
                        "max": "512"
                    },
                    "sample_control": {
                        "primitives_enabled": {
                            "page_table": true,
                            "page_fault": false
                        },
                        "sample_filters": []
                    },
                    "schemes": []
                }
            ]
        }
    ]
}"""

    with open("kdamonds.json", 'w') as FILE:
        FILE.writelines(string)