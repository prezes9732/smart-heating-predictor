# Smart Heating Predictor Configuration Flow
# Author: prezes9732
# Full implementation at: https://www.perplexity.ai/search/stworz-mi-custom-integration-d-4WuaNPQWQ.u3BH4ciKFAtw

from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN

class SmartHeatingPredictorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Heating Predictor."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Smart Heating Predictor", data=user_input)
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
