"""
全局异常处理中间件

拦截所有未捕获的异常，返回统一格式的 JSON 响应。
"""

import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from schemas.response import ApiResponse


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """统一异常处理中间件"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content=ApiResponse.fail(error=str(e)),
            )
        except PermissionError as e:
            return JSONResponse(
                status_code=403,
                content=ApiResponse.fail(error=str(e)),
            )
        except Exception as e:
            # 生产环境可以关闭 traceback 日志
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content=ApiResponse.fail(error=f"服务器内部错误: {str(e)}"),
            )