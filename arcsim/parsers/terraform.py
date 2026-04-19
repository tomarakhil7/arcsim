"""Terraform HCL parser"""

import hcl2
from typing import List, Dict


class TerraformParser:
    """Parse Terraform HCL files"""

    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse Terraform file and extract resources

        Args:
            filepath: Path to .tf file

        Returns:
            List of resource dicts with type, name, and config
        """
        with open(filepath, 'r') as f:
            tf_dict = hcl2.load(f)

        resources = []

        # Extract resources
        for resource_block in tf_dict.get('resource', []):
            for resource_type, resource_configs in resource_block.items():
                for resource_name, resource_config in resource_configs.items():
                    # Strip quotes from resource type and name (HCL2 parser artifact)
                    resource_type_clean = str(resource_type).strip('"').strip("'")
                    resource_name_clean = str(resource_name).strip('"').strip("'")

                    resources.append({
                        'type': resource_type_clean,
                        'name': resource_name_clean,
                        'config': resource_config
                    })

        return resources

    def get_environment_from_tags(self, resource: Dict) -> str:
        """Extract environment from tags

        Args:
            resource: Resource dict from parse_file

        Returns:
            Environment string: 'production', 'staging', or 'unknown'
        """
        config = resource.get('config', {})

        # Tags can be a list or dict depending on HCL2 parsing
        tags = config.get('tags', [])
        if isinstance(tags, list) and len(tags) > 0:
            tags = tags[0]
        elif not isinstance(tags, dict):
            tags = {}

        # Check for environment tag
        env = tags.get('Environment', tags.get('environment', tags.get('env', '')))

        if env:
            # Remove quotes if HCL2 parser left them
            env_str = str(env).strip('"').strip("'").lower()
            if env_str in ['prod', 'production']:
                return 'production'
            elif env_str in ['staging', 'stage']:
                return 'staging'

        return 'unknown'
