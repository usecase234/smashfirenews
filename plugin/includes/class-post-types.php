<?php
/**
 * Local content types for the plugin's mirrored editorial state.
 *
 * `smashfire_submission` mirrors the Hub's canonical submission record
 * so the Incoming/Drafts screens have something local and searchable to
 * query — the Hub (not this CPT) is the source of truth once Phase 3 wires
 * up the REST proxy. There is no `smashfire_pr_draft_version` CPT: the doc
 * calls that one "preferably Hub-owned ... mirrored locally as needed",
 * and nothing needs a local copy yet.
 *
 * Post type name is capped at 20 characters by WordPress
 * (register_post_type() truncates/rejects anything longer with a
 * `_doing_it_wrong` notice) — `smashfire_pr_submission` (23 chars) was over
 * that limit, so this is `smashfire_submission` (20 chars) instead.
 *
 * `smashfire_pr_asset` is deliberately NOT a CPT. Per the source plan's
 * "Suggested local entities" table, asset/rights metadata is high-volume
 * and better suited to a dedicated table than postmeta bloat — see
 * class-asset-table.php for that schema decision.
 *
 * Neither type is public or has a native edit screen: the editorial
 * workflow lives entirely under the plugin's own "Smashfire PR" admin
 * menu (see class-admin-menu.php), not in core Add New/Edit Post screens.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Smashfire_PR_Post_Types {

	public const SUBMISSION = 'smashfire_submission';

	public static function register(): void {
		add_action( 'init', array( __CLASS__, 'register_post_types' ) );
	}

	public static function register_post_types(): void {
		register_post_type(
			self::SUBMISSION,
			array(
				'label'           => 'Smashfire PR Submissions',
				'public'          => false,
				'show_ui'         => false,
				'show_in_menu'    => false,
				'show_in_rest'    => false,
				'has_archive'     => false,
				'rewrite'         => false,
				'capability_type' => 'post',
				'supports'        => array( 'title', 'editor', 'custom-fields' ),
			)
		);
	}
}
