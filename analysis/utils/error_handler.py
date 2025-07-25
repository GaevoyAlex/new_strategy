import logging

logger = logging.getLogger('trading_analysis')

class ErrorHandler:
    @staticmethod
    def handle_binance_error(error):
        error_msg = str(error)
        
        if "429" in error_msg or "rate limit" in error_msg.lower():
            logger.error("Binance rate limit exceeded")
            return {
                "error": "Rate limit exceeded",
                "retry_after": 60,
                "error_code": "RATE_LIMIT"
            }
        elif "400" in error_msg or "invalid" in error_msg.lower():
            logger.error(f"Invalid Binance request: {error_msg}")
            return {
                "error": "Invalid symbol or parameters",
                "error_code": "INVALID_REQUEST"
            }
        elif "404" in error_msg:
            logger.error(f"Binance endpoint not found: {error_msg}")
            return {
                "error": "Symbol not found",
                "error_code": "NOT_FOUND"
            }
        else:
            logger.error(f"Binance API error: {error_msg}")
            return {
                "error": "Binance API unavailable",
                "error_code": "API_ERROR"
            }

    @staticmethod
    def handle_claude_error(error):
        error_msg = str(error)
        
        if "rate" in error_msg.lower() and "limit" in error_msg.lower():
            logger.error("Claude API rate limit exceeded")
            return {
                "error": "Claude API rate limit exceeded",
                "retry_after": 30,
                "error_code": "CLAUDE_RATE_LIMIT"
            }
        elif "api" in error_msg.lower() and "key" in error_msg.lower():
            logger.error("Invalid Claude API key")
            return {
                "error": "Invalid API key",
                "error_code": "INVALID_API_KEY"
            }
        elif "timeout" in error_msg.lower():
            logger.error("Claude API timeout")
            return {
                "error": "Analysis request timeout",
                "error_code": "TIMEOUT"
            }
        else:
            logger.error(f"Claude API error: {error_msg}")
            return {
                "error": "Analysis generation failed",
                "error_code": "ANALYSIS_ERROR"
            }

    @staticmethod
    def handle_analysis_error(error, method):
        error_msg = str(error)
        logger.error(f"Analysis error [{method}]: {error_msg}")
        
        return {
            "error": f"Failed to perform {method} analysis",
            "details": error_msg,
            "error_code": "ANALYSIS_FAILED"
        }

    @staticmethod
    def handle_data_processing_error(error):
        error_msg = str(error)
        logger.error(f"Data processing error: {error_msg}")
        
        return {
            "error": "Failed to process market data",
            "details": error_msg,
            "error_code": "DATA_PROCESSING_ERROR"
        }