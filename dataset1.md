Feature Name,Description
dur,Total record duration (seconds).
proto,"Transaction protocol (e.g., TCP, UDP, ICMP)."
service,"Specific service used (e.g., http, ftp, ssh, dns)."
state,"State of the connection (e.g., CON - connected, FIN - finished)."
spkts / dpkts,Count of packets sent from source to destination / destination to source.
sbytes / dbytes,Total bytes sent from source to destination / destination to source.
rate,Overall packet transmission rate (packets per second).
sload / dload,Throughput (bits per second) for source / destination.
sloss / dloss,Number of packets dropped or retransmitted for source / destination.
sinpkt / dinpkt,Average time between two packets (inter-packet arrival time).
sjit / djit,Packet jitter (variation in arrival time) for source / destination.
swin / dwin,TCP window advertisement value for source / destination.
stcpb / dtcpb,TCP base sequence numbers used for tracking the flow.
tcprtt,Round Trip Time (RTT)—the time taken for a full TCP handshake.
synack,Time taken from the SYN packet to the SYN-ACK response.
ackdat,Time taken from the SYN-ACK to the final ACK in a handshake.
smean / dmean,Average (mean) packet size transmitted by source / destination.
trans_depth,Depth of the HTTP request/response pipeline.
response_body_len,Total length of the content in an HTTP response.
ct_src_dport_ltm,Connections to the same destination port from the same source in the last 100 flows.
ct_dst_sport_ltm,Connections from the same source port to the same destination in the last 100 flows.
is_ftp_login,"Binary (1 if an FTP login session is identified, else 0)."
ct_ftp_cmd,Count of FTP commands sent during a session.
ct_flw_http_mthd,Number of HTTP methods (GET/POST) used in the flow.
is_sm_ips_ports,Binary (1 if source and destination IP/Ports are the same).
attack_cat,"Categorical classification of the attack type (e.g., DoS, Fuzzers)."
label,"Binary target variable (0 for Normal, 1 for Attack)."

