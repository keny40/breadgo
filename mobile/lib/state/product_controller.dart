import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import '../models/product.dart';

class ProductController extends ChangeNotifier {
  ProductController({required this.apiClient});

  final ApiClient apiClient;

  List<Product> products = [];
  bool loading = false;
  String? errorMessage;
  String sido = '서울특별시';
  String sigungu = '강남구';
  String dong = '역삼동';

  Future<void> loadProducts({
    String? nextSido,
    String? nextSigungu,
    String? nextDong,
  }) async {
    sido = nextSido ?? sido;
    sigungu = nextSigungu ?? sigungu;
    dong = nextDong ?? dong;
    loading = true;
    errorMessage = null;
    notifyListeners();

    try {
      products = await apiClient.fetchRegionProducts(
        sido: sido,
        sigungu: sigungu,
        dong: dong,
      );
    } on ApiException catch (error) {
      errorMessage = error.message;
    } catch (_) {
      errorMessage = '상품을 불러오지 못했습니다. API 주소와 네트워크 상태를 확인해 주세요.';
    } finally {
      loading = false;
      notifyListeners();
    }
  }
}
