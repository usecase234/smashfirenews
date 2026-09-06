<?php
/**
 * Plugin Name: Smashfire PR
 * Description: AI newsroom intake and editorial queue. Thin client for the
 *              independently-deployed Smashfire PR Hub — no LLM provider
 *              credentials ever live in this plugin.
 * Version: 0.0.1
 * Requires PHP: 8.1
 *
 * Phase 2: CPT registration + Hub client. See
 * docs/Smashfire_PR_Starting_Build_Plan.md for the phase sequence.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // No direct access.
}

define( 'SMASHFIRE_PR_VERSION', '0.0.1' );
define( 'SMASHFIRE_PR_DIR', plugin_dir_path( __FILE__ ) );

require_once SMASHFIRE_PR_DIR . 'includes/class-hub-client.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-admin-menu.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-post-types.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-asset-table.php';

Smashfire_PR_Asset_Table::register_activation_hook( __FILE__ );

/**
 * Boot the plugin. Still no submission form or REST proxying — that's
 * Phase 3 — this just registers the local content types and admin menu.
 */
function smashfire_pr_bootstrap(): void {
	Smashfire_PR_Admin_Menu::register();
	Smashfire_PR_Post_Types::register();
}
add_action( 'plugins_loaded', 'smashfire_pr_bootstrap' );
