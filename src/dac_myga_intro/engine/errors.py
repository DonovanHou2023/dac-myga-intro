class ProductCatalogError(Exception):
    pass


class ProductNotFoundError(ProductCatalogError):
    pass


class ProductSpecValidationError(ProductCatalogError):
    pass