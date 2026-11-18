# Kiểm định judge

Tôi đối chiếu kết quả judge với nhãn người trong hai bộ CSV công khai. FAIL được xem là lớp dương vì mục tiêu là tìm lỗi. Judge chỉ được dùng khi đồng thời đạt κ ≥ 0.6, precision ≥ 0.8 và recall ≥ 0.7.

| Judge | n | κ | P | R | TP/FP/FN/TN | Quyết định |
|---|---:|---:|---:|---:|---|---|
| tone | 100 | 0.757 | 0.857 | 0.8 | 24/4/6/66 | Dùng cho tone |
| helpful | 100 | 0.375 | 1.0 | 0.3 | 9/0/21/70 | Loại khỏi gate |

## Phân tích các trường hợp bất đồng

Bảng dưới ghi lại cách tôi đối chiếu câu trả lời với tiêu chí chấm. Đây là phân tích trên dữ liệu công khai, chưa phải một bộ nhãn độc lập mới.

| Case | Judge / người | Nhận định | Sửa rubric |
|---|---|---|---|
| H-008 | PASS / FAIL | Người đúng: cách xưng hô và câu 'anh check' quá suồng sã. | Nêu ví dụ FAIL cho nha, check và cách xưng hô thiếu trang trọng. |
| H-017 | PASS / FAIL | Người đúng: 'bạn ơi', 'rồi nha' không phù hợp giọng hỗ trợ quy định. | Chấm cả câu; không cho PASS chỉ vì có chữ Dạ. |
| H-029 | PASS / FAIL | Người đúng: 'không cần nhắn thêm' có tính gạt bỏ người dùng. | Thêm tiêu chí không ra lệnh hoặc ngăn người dùng hỏi tiếp. |
| H-042 | FAIL / PASS | Người đúng: thông báo rõ, trung tính và có thời gian dự kiến. | Cho phép câu ngắn lịch sự; không bắt buộc lời xin lỗi ở mọi phản hồi. |
| H-051 | FAIL / PASS | Người đúng về tone: câu lịch sự dù có từ refund. | Tách sở thích thuần Việt khỏi tiêu chí lịch sự; không dùng tone để xác nhận tiền. |
| HL-015 | PASS / FAIL | Giữ nhãn người cho helpful; chỉ câu đã hoàn tiền chưa đủ xác minh tác vụ. | Cần context yêu cầu, ledger và hành động; không suy ra đúng chỉ từ lời xác nhận. |

## Quyết định sử dụng

Tôi giữ tone cho việc đánh giá giọng điệu vì cả ba chỉ số đều đạt ngưỡng. Tuy nhiên, judge này vẫn bỏ sót lỗi. Với helpful, precision bằng 1.0 nhưng recall chỉ 0.3 và κ bằng 0.375: 21 trong 30 lỗi không được phát hiện. Vì vậy, tôi loại helpful khỏi gate. Số tiền và approval được kiểm tra bằng code.

Rogan–Gladen hiệu chỉnh fail rate của cả hai bộ về 0.3; hiệu chỉnh tỷ lệ không làm classifier đủ đáng tin.

Giới hạn: replay công khai, nhãn người không mặc nhiên hoàn hảo; một số helpful case thiếu context nên cần phân xử với yêu cầu gốc. Các sửa rubric là đề xuất, chưa có đo lại trên held-out.
