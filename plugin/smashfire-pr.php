<?php
/**
 * Plugin Name: Smashfire PR
 * Description: AI newsroom intake and editorial queue. Thin client for the
 *              independently-deployed Smashfire PR Hub — no LLM provider
 *              credentials ever live in this plugin.
 * Version: 0.0.1
 * Requires PHP: 8.1
 *
 * Phase 0: bootstrap + empty admin menu only. See
 * docs/Smashfire_PR_Starting_Build_Plan.md for the phase sequence.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // No direct access.
}

define( 'SMASHFIRE_PR_VERSION', '0.0.1' );
define( 'SMASHFIRE_PR_DIR', plugin_dir_path( __FILE__ ) );

require_once SMASHFIRE_PR_DIR . 'includes/class-hub-client.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-admin-menu.php';

/**
 * Boot the plugin. Kept intentionally tiny in Phase 0 — CPT registration,
 * the real submission form, and REST routes arrive in Phase 2/3.
 */
function smashfire_pr_bootstrap(): void {
	Smashfire_PR_Admin_Menu::register();
}
add_action( 'plugins_loaded', 'smashfire_pr_bootstrap' );
